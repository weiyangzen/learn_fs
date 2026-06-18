# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-starfive-jh7100.h

Purpose: `pinctrl-starfive-jh7100.h` is a Devicetree binding header for a pin controller. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 244 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are GPO_SDIO0 (30),
GPO_SDIO1 (30), GPO_PWM (16), GPI_SDIO0 (11), GPI_SDIO1 (11), GPO_SPI2AHB (8), GPO_I2STX (7),
GPI_SPI2AHB (6), GPO_I2SRX (5), GPO_SPI0 (5). Representative constants are `PAD_GPIO_OFFSET`,
`PAD_FUNC_SHARE_OFFSET`, `GPO_REVERSE`, `GPO_LOW`, `GPO_HIGH`, `GPO_ENABLE`, `GPO_DISABLE`,
`GPO_CLK_GMAC_PAPHYREF`, `...`, `GPI_UART2_PAD_CTS_N`, `GPI_UART2_PAD_DCD_N`, `GPI_UART2_PAD_DSR_N`,
`GPI_UART2_PAD_RI_N`, `GPI_UART2_PAD_SIN`, `GPI_UART3_PAD_SIN`, `GPI_USB_OVER_CURRENT`, `GPI_NONE`.
Function-like helpers are `PAD_GPIO`, `PAD_FUNC_SHARE`, `GPIOMUX`. Value shape: literal numeric
range 0..2147483648 across 215 macros; 28 alias or symbol-derived values; 1 expression values; 3
function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_STARFIVE_JH7100_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `GPO_SDIO0 group`, `GPO_SDIO1 group`, `GPO_PWM group`, `GPI_SDIO0 group`, `GPI_SDIO1
group`, `GPO_SPI2AHB group`, `GPO_I2STX group`, `GPI_SPI2AHB group`, `GPO_I2SRX group`, `GPO_SPI0
group`, `GPO_SPI1 group`, `GPO_SPI2 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 275 lines long. Notable source comments include `GPIOMUX bits: | 31 - 24 | 23 - 16 | 15
- 8 | 7 | 6 | 5 - 0 | | dout | doen | din | dout rev | doen rev | gpio nr | dout: output signal
doen: output enable signal din: optional input signal, 0xff = none dout rev: output signal reverse
bit doen rev: output enable signal reverse bit gpio nr: gpio number, 0 - 63`,
`__DT_BINDINGS_PINCTRL_STARFIVE_JH7100_H__`. Example value clusters are GPO_SDIO0:
`GPO_SDIO0_PAD_CARD_POWER_EN=53`, `GPO_SDIO0_PAD_CCLK_OUT=54`, `GPO_SDIO0_PAD_CCMD_OE=55`,
`GPO_SDIO0_PAD_CCMD_OEN=(GPO_SDIO0_PAD_CCMD_OE | GPO_REVERSE)`; GPO_SDIO1:
`GPO_SDIO1_PAD_CARD_POWER_EN=74`, `GPO_SDIO1_PAD_CCLK_OUT=75`, `GPO_SDIO1_PAD_CCMD_OE=76`,
`GPO_SDIO1_PAD_CCMD_OEN=(GPO_SDIO1_PAD_CCMD_OE | GPO_REVERSE)`; GPO_PWM: `GPO_PWM_PAD_OE_N_BIT0=29`,
`GPO_PWM_PAD_OE_N_BIT1=30`, `GPO_PWM_PAD_OE_N_BIT2=31`, `GPO_PWM_PAD_OE_N_BIT3=32`; GPI_SDIO0:
`GPI_SDIO0_PAD_CARD_DETECT_N=25`, `GPI_SDIO0_PAD_CARD_WRITE_PRT=26`, `GPI_SDIO0_PAD_CCMD_IN=27`,
`GPI_SDIO0_PAD_CDATA_IN_BIT0=28`; GPI_SDIO1: `GPI_SDIO1_PAD_CARD_DETECT_N=36`,
`GPI_SDIO1_PAD_CARD_WRITE_PRT=37`, `GPI_SDIO1_PAD_CCMD_IN=38`, `GPI_SDIO1_PAD_CDATA_IN_BIT0=39`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `PAD_GPIO_OFFSET`, `PAD_FUNC_SHARE_OFFSET`, `PAD_GPIO`, `PAD_FUNC_SHARE`, `GPIOMUX`,
`GPO_REVERSE`, `GPO_LOW`, `GPO_HIGH`. Test signals include dt_binding_check coverage, DTS compile
coverage for each SoC, pinctrl probe logs, GPIO loopback, and peripheral bring-up using
representative mux groups.
