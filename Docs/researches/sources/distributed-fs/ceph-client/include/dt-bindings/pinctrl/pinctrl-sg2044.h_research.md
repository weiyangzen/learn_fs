# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2044.h

Purpose: `pinctrl-sg2044.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 208 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are PIN_RGMII0 (16),
PIN_SPIF0 (8), PIN_SPIF1 (8), PIN_BOOT (8), PIN_PCIE0 (6), PIN_PCIE1 (6), PIN_PCIE2 (6), PIN_PCIE3
(6), PIN_PCIE4 (6), PIN_JTAG0 (6). Representative constants are `PIN_IIC0_SMBSUS_IN`,
`PIN_IIC0_SMBSUS_OUT`, `PIN_IIC0_SMBALERT`, `PIN_IIC1_SMBSUS_IN`, `PIN_IIC1_SMBSUS_OUT`,
`PIN_IIC1_SMBALERT`, `PIN_IIC2_SMBSUS_IN`, `PIN_IIC2_SMBSUS_OUT`, `...`, `PIN_XTAL_32K`,
`PIN_SYS_RST`, `PIN_PWR_BUTTON`, `PIN_TEST_EN`, `PIN_TEST_MODE_MBIST`, `PIN_TEST_MODE_SCAN`,
`PIN_TEST_MODE_BSD`, `PIN_BISR_BYP`. Function-like helpers are `PINMUX`. Value shape: literal
numeric range 0..206 across 207 macros; 1 expression values; 1 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_SG2044_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PIN_RGMII0 group`, `PIN_SPIF0 group`, `PIN_SPIF1 group`, `PIN_BOOT group`, `PIN_PCIE0 group`,
`PIN_PCIE1 group`, `PIN_PCIE2 group`, `PIN_PCIE3 group`, `PIN_PCIE4 group`, `PIN_JTAG0 group`,
`PIN_JTAG1 group`, `PIN_JTAG2 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 221 lines long. Notable source comments include `_DT_BINDINGS_PINCTRL_SG2044_H`. Example
value clusters are PIN_RGMII0: `PIN_RGMII0_TXD0=66`, `PIN_RGMII0_TXD1=67`, `PIN_RGMII0_TXD2=68`,
`PIN_RGMII0_TXD3=69`; PIN_SPIF0: `PIN_SPIF0_CLK_SEL1=42`, `PIN_SPIF0_CLK_SEL0=43`,
`PIN_SPIF0_WP=44`, `PIN_SPIF0_HOLD=45`; PIN_SPIF1: `PIN_SPIF1_CLK_SEL1=50`, `PIN_SPIF1_CLK_SEL0=51`,
`PIN_SPIF1_WP=52`, `PIN_SPIF1_HOLD=53`; PIN_BOOT: `PIN_BOOT_SEL0=183`, `PIN_BOOT_SEL1=184`,
`PIN_BOOT_SEL2=185`, `PIN_BOOT_SEL3=186`; PIN_PCIE0: `PIN_PCIE0_L0_RESET=12`,
`PIN_PCIE0_L1_RESET=13`, `PIN_PCIE0_L0_WAKEUP=14`, `PIN_PCIE0_L1_WAKEUP=15`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `PINMUX`, `PIN_IIC0_SMBSUS_IN`, `PIN_IIC0_SMBSUS_OUT`, `PIN_IIC0_SMBALERT`,
`PIN_IIC1_SMBSUS_IN`, `PIN_IIC1_SMBSUS_OUT`, `PIN_IIC1_SMBALERT`, `PIN_IIC2_SMBSUS_IN`. Test signals
include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO
loopback, and peripheral bring-up using representative mux groups.
