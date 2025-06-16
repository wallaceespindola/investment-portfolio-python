import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

TITLE_IBOV = 'IBOV'
TITLE_PL_TOTAL = 'PL Total'
INDICE_BOVESPA = '^BVSP'
CAMPO_CLOSE = 'Close'  # PRECO DE FECHAMENTO


def simulacao_carteira(inicio, fim, carteira):
    precos = yf.download(list(carteira.keys()), start=inicio, end=fim, progress=False)
    print(f'Precos:\n{precos}')
    # Precos:
    # Price[0]     Close[1]   High[2]    Low[3]     Open[4]   Volume[5]
    # Ticker       PETR4.SA   PETR4.SA   PETR4.SA   PETR4.SA  PETR4.SA
    # Date
    # 2025-01-02  34.877396  35.180924  34.327247  34.545408  30046800
    # 2025-01-03  34.507469  35.133498  34.450556  34.981733  23314200

    precos = yf.download(list(carteira.keys()), start=inicio, end=fim, progress=False)[CAMPO_CLOSE]
    print(f'Precos Filtrado por Close:\n{precos}')

    primeiro = precos.iloc[0]  # para normalizar o PL
    compras_df = pd.Series(data=carteira, index=list(carteira.keys()))
    qtd_acoes = compras_df / primeiro  # qtd de acoes a serem compradas (normalizando)
    qtd_acoes = round(qtd_acoes, 0)
    PL = precos * qtd_acoes
    PL[TITLE_PL_TOTAL] = PL.sum(axis=1)
    print(f'PL filtrado por Close:\n{PL}')  # ATENCAO, FOI FILTRADO

    ibov = yf.download(INDICE_BOVESPA, start=inicio, end=fim, progress=False)
    print(f'IBOV:\n{ibov}')
    ibov.rename(columns={INDICE_BOVESPA: TITLE_IBOV}, inplace=True)

    ibov.drop(ibov.columns[[1, 2, 3, 4]], axis=1, inplace=True)  # REMOVE AS COLUNAS NÃO USADAS (SO O CLOSE FICA)

    # Remove MultiIndex se houver
    if isinstance(ibov.columns, pd.MultiIndex):
        ibov.columns = ibov.columns.droplevel(0)

    # Reset Index IBOV
    ibov.reset_index(inplace=True)

    # Reset Index PL
    PL.reset_index(inplace=True)

    # Merge
    print(f'==> IBOV filtrado por Close:\n{ibov}')
    print(f'==> PL filtrado por Close:\n{PL}')

    consolidado = pd.merge(ibov, PL, how='inner', on='Date')
    print(f'==> Consolidado:\n{consolidado}')

    # Normaliza apenas os dados numéricos
    colunas_numericas = consolidado.select_dtypes(include='number').columns
    consolidado_adj = consolidado[colunas_numericas] / consolidado[colunas_numericas].iloc[0]  # normaliza

    # Restaura a coluna de data para visualização
    consolidado_adj['Date'] = consolidado['Date']
    print(f'consolidado_adj:\n{consolidado_adj}')

    # Plota o consolidado
    consolidado_adj.set_index('Date')[[TITLE_IBOV, TITLE_PL_TOTAL]].plot(figsize=(8, 6));  # IBOV x PL total da carteira
    plt.title('Evolução Normalizada da Carteira (PL) vs IBOV')
    plt.xlabel('Data')
    plt.ylabel('Variação Normalizada')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plota tudo junto
    consolidado_adj.set_index('Date').plot(figsize=(8, 6));  # tudo junto
    plt.title('Evolução Normalizada da Carteira (PL) vs IBOV vs Acoes Individuais')
    plt.xlabel('Data')
    plt.ylabel('Variação Normalizada')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    inicio = '2025-01-01'
    fim = '2025-06-15'
    # Exemplo de portfolio
    portfolio = {
        'PETR4.SA': 1000,
        'ITUB4.SA': 1000,
        'WEGE3.SA': 1000,
        'VALE3.SA': 1000,
    }
    simulacao_carteira(inicio, fim, portfolio)
