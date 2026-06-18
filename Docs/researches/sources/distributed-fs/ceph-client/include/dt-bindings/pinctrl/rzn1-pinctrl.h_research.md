# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzn1-pinctrl.h

Purpose: `rzn1-pinctrl.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 108 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are RZN1 (108).
Representative constants are `RZN1_FUNC_HIGHZ`, `RZN1_FUNC_0L`, `RZN1_FUNC_CLK_ETH_MII_RGMII_RMII`,
`RZN1_FUNC_CLK_ETH_NAND`, `RZN1_FUNC_QSPI`, `RZN1_FUNC_SDIO`, `RZN1_FUNC_LCD`, `RZN1_FUNC_LCD_E`,
`...`, `RZN1_FUNC_MDIO1_E1_GMAC0`, `RZN1_FUNC_MDIO1_E1_GMAC1`, `RZN1_FUNC_MDIO1_E1_ECAT`,
`RZN1_FUNC_MDIO1_E1_S3_MDIO0`, `RZN1_FUNC_MDIO1_E1_S3_MDIO1`, `RZN1_FUNC_MDIO1_E1_HWRTOS`,
`RZN1_FUNC_MDIO1_E1_SWITCH`, `RZN1_FUNC_MAX`. Function-like helpers are `RZN1_PINMUX`. Value shape:
literal numeric range 0..9 across 10 macros; 97 alias or symbol-derived values; 1 expression values;
1 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RZN1_PINCTRL_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`These are MDIO0 peripherals for the RZN1_FUNC_ETH_MDIO function`, `These are MDIO0 peripherals for
the RZN1_FUNC_ETH_MDIO_E1 function`, `These are MDIO1 peripherals for the RZN1_FUNC_ETH_MDIO
function`, `These are MDIO1 peripherals for the RZN1_FUNC_ETH_MDIO_E1 function`, which is the
intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 141 lines long. Notable source comments include `Defines macros and constants for
Renesas RZ/N1 pin controller pin muxing functions.`, `Given the different levels of muxing on the
SoC, it was decided to 'linearize' them into one numerical space. So mux level 1, 2 and the MDIO
muxes are all represented by one single value. You can derive the hardware value pretty easily too,
as 0...9 are Level 1 10...71 are Level 2. The Level 2 mux will be set to this value -
RZN1_FUNC_L2_OFFSET, and the Level 1 mux will be set accordingly. 72...103 are for the 2 MDIO
muxes.`, `I'm Special`, `These are MDIO0 peripherals for the RZN1_FUNC_ETH_MDIO function`, `These
are MDIO0 peripherals for the RZN1_FUNC_ETH_MDIO_E1 function`, `These are MDIO1 peripherals for the
RZN1_FUNC_ETH_MDIO function`. Example value clusters are RZN1: `RZN1_PINMUX=\`, `RZN1_FUNC_HIGHZ=0`,
`RZN1_FUNC_0L=1`, `RZN1_FUNC_CLK_ETH_MII_RGMII_RMII=2`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZN1_PINMUX`, `RZN1_FUNC_HIGHZ`, `RZN1_FUNC_0L`,
`RZN1_FUNC_CLK_ETH_MII_RGMII_RMII`, `RZN1_FUNC_CLK_ETH_NAND`, `RZN1_FUNC_QSPI`, `RZN1_FUNC_SDIO`,
`RZN1_FUNC_LCD`. Test signals include dt_binding_check coverage, DTS compile coverage for each SoC,
pinctrl probe logs, GPIO loopback, and peripheral bring-up using representative mux groups.
