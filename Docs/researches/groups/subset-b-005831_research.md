# Research: subset-b-005831

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2044.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-sg2044.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-starfive-jh7100.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-starfive-jh7100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-tegra-io-pad.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-tegra-io-pad.h

Purpose: `pinctrl-tegra-io-pad.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are TEGRA (2). Representative
constants are `TEGRA_IO_PAD_VOLTAGE_1V8`, `TEGRA_IO_PAD_VOLTAGE_3V3`, `TEGRA_IO_PAD_VOLTAGE_1V8`,
`TEGRA_IO_PAD_VOLTAGE_3V3`. Function-like helpers are none. Value shape: literal numeric range 0..1
across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_TEGRA_IO_PAD_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Voltage levels of the I/O pad's source rail`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 18 lines long. Notable source comments include `pinctrl-tegra-io-pad.h: Tegra I/O pad
source voltage configuration constants pinctrl bindings.`, `Voltage levels of the I/O pad's source
rail`. Example value clusters are TEGRA: `TEGRA_IO_PAD_VOLTAGE_1V8=0`, `TEGRA_IO_PAD_VOLTAGE_3V3=1`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `TEGRA_IO_PAD_VOLTAGE_1V8`, `TEGRA_IO_PAD_VOLTAGE_3V3`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-tegra-io-pad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-tegra-xusb.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-tegra-xusb.h

Purpose: `pinctrl-tegra-xusb.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are TEGRA (2). Representative
constants are `TEGRA_XUSB_PADCTL_PCIE`, `TEGRA_XUSB_PADCTL_SATA`, `TEGRA_XUSB_PADCTL_PCIE`,
`TEGRA_XUSB_PADCTL_SATA`. Function-like helpers are none. Value shape: literal numeric range 0..1
across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_TEGRA_XUSB_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`TEGRA group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 8 lines long. Notable source comments include `_DT_BINDINGS_PINCTRL_TEGRA_XUSB_H`.
Example value clusters are TEGRA: `TEGRA_XUSB_PADCTL_PCIE=0`, `TEGRA_XUSB_PADCTL_SATA=1`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `TEGRA_XUSB_PADCTL_PCIE`, `TEGRA_XUSB_PADCTL_SATA`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-tegra-xusb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-tegra.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-tegra.h

Purpose: `pinctrl-tegra.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 13 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are TEGRA (13).
Representative constants are `TEGRA_PIN_DISABLE`, `TEGRA_PIN_ENABLE`, `TEGRA_PIN_PULL_NONE`,
`TEGRA_PIN_PULL_DOWN`, `TEGRA_PIN_PULL_UP`, `TEGRA_PIN_LP_DRIVE_DIV_8`, `TEGRA_PIN_LP_DRIVE_DIV_4`,
`TEGRA_PIN_LP_DRIVE_DIV_2`, `TEGRA_PIN_LP_DRIVE_DIV_8`, `TEGRA_PIN_LP_DRIVE_DIV_4`,
`TEGRA_PIN_LP_DRIVE_DIV_2`, `TEGRA_PIN_LP_DRIVE_DIV_1`, `TEGRA_PIN_SLEW_RATE_FASTEST`,
`TEGRA_PIN_SLEW_RATE_FAST`, `TEGRA_PIN_SLEW_RATE_SLOW`, `TEGRA_PIN_SLEW_RATE_SLOWEST`. Function-like
helpers are none. Value shape: literal numeric range 0..3 across 13 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_TEGRA_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are `Low
power mode driver`, `Rising/Falling slew rate`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 37 lines long. Notable source comments include `This header provides constants for Tegra
pinctrl bindings.`, `Enable/disable for diffeent dt properties. This is applicable for properties
nvidia,enable-input, nvidia,tristate, nvidia,open-drain, nvidia,lock, nvidia,rcv-sel, nvidia,high-
speed-mode, nvidia,schmitt.`, `Low power mode driver`, `Rising/Falling slew rate`. Example value
clusters are TEGRA: `TEGRA_PIN_DISABLE=0`, `TEGRA_PIN_ENABLE=1`, `TEGRA_PIN_PULL_NONE=0`,
`TEGRA_PIN_PULL_DOWN=1`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `TEGRA_PIN_DISABLE`, `TEGRA_PIN_ENABLE`, `TEGRA_PIN_PULL_NONE`,
`TEGRA_PIN_PULL_DOWN`, `TEGRA_PIN_PULL_UP`, `TEGRA_PIN_LP_DRIVE_DIV_8`, `TEGRA_PIN_LP_DRIVE_DIV_4`,
`TEGRA_PIN_LP_DRIVE_DIV_2`. Test signals include dt_binding_check coverage, DTS compile coverage for
each SoC, pinctrl probe logs, GPIO loopback, and peripheral bring-up using representative mux
groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-tegra.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-zynq.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-zynq.h

Purpose: `pinctrl-zynq.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 4 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are IO_STANDARD (4). Representative
constants are `IO_STANDARD_LVCMOS18`, `IO_STANDARD_LVCMOS25`, `IO_STANDARD_LVCMOS33`,
`IO_STANDARD_HSTL`, `IO_STANDARD_LVCMOS18`, `IO_STANDARD_LVCMOS25`, `IO_STANDARD_LVCMOS33`,
`IO_STANDARD_HSTL`. Function-like helpers are none. Value shape: literal numeric range 1..4 across 4
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_ZYNQ_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Configuration options for different power supplies`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 17 lines long. Notable source comments include `MIO pin configuration defines for Xilinx
Zynq`, `Configuration options for different power supplies`, `_DT_BINDINGS_PINCTRL_ZYNQ_H`. Example
value clusters are IO_STANDARD: `IO_STANDARD_LVCMOS18=1`, `IO_STANDARD_LVCMOS25=2`,
`IO_STANDARD_LVCMOS33=3`, `IO_STANDARD_HSTL=4`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `IO_STANDARD_LVCMOS18`, `IO_STANDARD_LVCMOS25`, `IO_STANDARD_LVCMOS33`,
`IO_STANDARD_HSTL`. Test signals include dt_binding_check coverage, DTS compile coverage for each
SoC, pinctrl probe logs, GPIO loopback, and peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-zynq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-zynqmp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-zynqmp.h

Purpose: `pinctrl-zynqmp.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 4 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are IO_STANDARD (2), SLEW (2).
Representative constants are `IO_STANDARD_LVCMOS33`, `IO_STANDARD_LVCMOS18`, `SLEW_RATE_FAST`,
`SLEW_RATE_SLOW`, `IO_STANDARD_LVCMOS33`, `IO_STANDARD_LVCMOS18`, `SLEW_RATE_FAST`,
`SLEW_RATE_SLOW`. Function-like helpers are none. Value shape: literal numeric range 0..1 across 4
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_ZYNQMP_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Bit value for different voltage levels`, `Bit values for Slew Rates`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 19 lines long. Notable source comments include `MIO pin configuration defines for Xilinx
ZynqMP`, `Bit value for different voltage levels`, `Bit values for Slew Rates`,
`_DT_BINDINGS_PINCTRL_ZYNQMP_H`. Example value clusters are IO_STANDARD: `IO_STANDARD_LVCMOS33=0`,
`IO_STANDARD_LVCMOS18=1`; SLEW: `SLEW_RATE_FAST=0`, `SLEW_RATE_SLOW=1`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `IO_STANDARD_LVCMOS33`, `IO_STANDARD_LVCMOS18`, `SLEW_RATE_FAST`, `SLEW_RATE_SLOW`.
Test signals include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe
logs, GPIO loopback, and peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pinctrl-zynqmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/qcom,pmic-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/qcom,pmic-gpio.h

Purpose: `qcom,pmic-gpio.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 116 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are PM8058 (22), PMIC_GPIO
(18), PM8038 (15), PM8917 (12), PM8941 (12), PMA8084 (11), PM8916 (9), PM8018 (7), PM8921 (7),
PM8994 (3). Representative constants are `PMIC_GPIO_PULL_UP_30`, `PMIC_GPIO_PULL_UP_1P5`,
`PMIC_GPIO_PULL_UP_31P5`, `PMIC_GPIO_PULL_UP_1P5_30`, `PMIC_GPIO_STRENGTH_NO`,
`PMIC_GPIO_STRENGTH_HIGH`, `PMIC_GPIO_STRENGTH_MED`, `PMIC_GPIO_STRENGTH_LOW`, `...`,
`PM8941_GPIO33_36_LPG_DRV_HI`, `PMA8084_GPIO4_5_LPG_DRV`, `PMA8084_GPIO7_10_LPG_DRV`,
`PMA8084_GPIO5_14_KEYP_DRV`, `PMA8084_GPIO19_21_KEYP_DRV`, `PMA8084_GPIO15_18_DIV_CLK`,
`PMA8084_GPIO15_18_SLEEP_CLK`, `PMA8084_GPIO22_BAT_ALRM_OUT`. Function-like helpers are none. Value
shape: literal numeric range 0..7 across 57 macros; 59 alias or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_QCOM_PMIC_GPIO_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `To be used with "function"`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 164 lines long. Notable source comments include `This header provides constants for the
Qualcomm PMIC GPIO binding.`, `Note: PM8018 GPIO3 and GPIO4 are supporting only S3 and L2 options
(1.8V)`, `Note: PM8038 GPIO7 and GPIO8 are supporting only L11 and L4 options (1.8V)`, `Note: PM8916
GPIO1 and GPIO2 are supporting only L2(1.15V) and L5(1.8V) options`, `Note: PM8941 gpios from 15 to
18 are supporting only S3 and L6 options (1.8V)`, `Note: PMA8084 gpios from 15 to 18 are supporting
only S4 and L6 options (1.8V)`. Example value clusters are PM8058: `PM8058_GPIO_VPH=0`,
`PM8058_GPIO_BB=1`, `PM8058_GPIO_S3=2`, `PM8058_GPIO_L3=3`; PMIC_GPIO: `PMIC_GPIO_PULL_UP_30=0`,
`PMIC_GPIO_PULL_UP_1P5=1`, `PMIC_GPIO_PULL_UP_31P5=2`, `PMIC_GPIO_PULL_UP_1P5_30=3`; PM8038:
`PM8038_GPIO_VPH=0`, `PM8038_GPIO_BB=1`, `PM8038_GPIO_L11=2`, `PM8038_GPIO_L15=3`; PM8917:
`PM8917_GPIO_VPH=0`, `PM8917_GPIO_S4=2`, `PM8917_GPIO_L15=3`, `PM8917_GPIO_L4=4`; PM8941:
`PM8941_GPIO_VPH=0`, `PM8941_GPIO_L1=1`, `PM8941_GPIO_S3=2`, `PM8941_GPIO_L6=3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `PMIC_GPIO_PULL_UP_30`, `PMIC_GPIO_PULL_UP_1P5`, `PMIC_GPIO_PULL_UP_31P5`,
`PMIC_GPIO_PULL_UP_1P5_30`, `PMIC_GPIO_STRENGTH_NO`, `PMIC_GPIO_STRENGTH_HIGH`,
`PMIC_GPIO_STRENGTH_MED`, `PMIC_GPIO_STRENGTH_LOW`. Test signals include dt_binding_check coverage,
DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and peripheral bring-up using
representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/qcom,pmic-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/qcom,pmic-mpp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/qcom,pmic-mpp.h

Purpose: `qcom,pmic-mpp.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 67 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are PMIC_MPP (22), PM8018
(7), PM8038 (6), PM8901 (5), PM8058 (4), PM8921 (4), PM8941 (4), PMA8084 (4), PM8994 (4), PM8916
(3). Representative constants are `PM8058_MPP_VPH`, `PM8058_MPP_S3`, `PM8058_MPP_L2`,
`PM8058_MPP_L3`, `PM8901_MPP_MSMIO`, `PM8901_MPP_DIG`, `PM8901_MPP_L5`, `PM8901_MPP_S4`, `...`,
`PMIC_MPP_AOUT_LVL_ABUS2`, `PMIC_MPP_AOUT_LVL_ABUS3`, `PMIC_MPP_FUNC_NORMAL`,
`PMIC_MPP_FUNC_PAIRED`, `PMIC_MPP_FUNC_DTEST1`, `PMIC_MPP_FUNC_DTEST2`, `PMIC_MPP_FUNC_DTEST3`,
`PMIC_MPP_FUNC_DTEST4`. Function-like helpers are none. Value shape: literal numeric range 0..7
across 61 macros; 6 alias or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_QCOM_PMIC_MPP_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `power-source`, `Digital Input/Output: level [PM8058]`, `Digital Input/Output: level [PM8901]`,
`Digital Input/Output: level [PM8921]`, `Digital Input/Output: level [PM8821]`, `Digital
Input/Output: level [PM8018]`, `Digital Input/Output: level [PM8038]`, `Only supported for
MPP_05-MPP_08`, `Analog Output: level`, `To be used with "function"`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 106 lines long. Notable source comments include `This header provides constants for the
Qualcomm PMIC's Multi-Purpose Pin binding.`, `power-source`, `Digital Input/Output: level [PM8058]`,
`Digital Input/Output: level [PM8901]`, `Digital Input/Output: level [PM8921]`, `Digital
Input/Output: level [PM8821]`. Example value clusters are PMIC_MPP: `PMIC_MPP_AMUX_ROUTE_CH5=0`,
`PMIC_MPP_AMUX_ROUTE_CH6=1`, `PMIC_MPP_AMUX_ROUTE_CH7=2`, `PMIC_MPP_AMUX_ROUTE_CH8=3`; PM8018:
`PM8018_MPP_L4=0`, `PM8018_MPP_L14=1`, `PM8018_MPP_S3=2`, `PM8018_MPP_L6=3`; PM8038:
`PM8038_MPP_L20=0`, `PM8038_MPP_L11=1`, `PM8038_MPP_L5=2`, `PM8038_MPP_L15=3`; PM8901:
`PM8901_MPP_MSMIO=0`, `PM8901_MPP_DIG=1`, `PM8901_MPP_L5=2`, `PM8901_MPP_S4=3`; PM8058:
`PM8058_MPP_VPH=0`, `PM8058_MPP_S3=1`, `PM8058_MPP_L2=2`, `PM8058_MPP_L3=3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `PM8058_MPP_VPH`, `PM8058_MPP_S3`, `PM8058_MPP_L2`, `PM8058_MPP_L3`,
`PM8901_MPP_MSMIO`, `PM8901_MPP_DIG`, `PM8901_MPP_L5`, `PM8901_MPP_S4`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/qcom,pmic-mpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/r7s72100-pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/r7s72100-pinctrl.h

Purpose: `r7s72100-pinctrl.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are RZA1 (2). Representative
constants are `RZA1_PINS_PER_PORT`, `RZA1_PINS_PER_PORT`. Function-like helpers are `RZA1_PINMUX`.
Value shape: literal numeric range 16..16 across 1 macros; 1 alias or symbol-derived values; 1
function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_RENESAS_RZA1_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RZA1 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 17 lines long. Notable source comments include `Defines macros and constants for Renesas
RZ/A1 pin controller pin muxing functions.`, `Create the pin index from its bank and position
numbers and store in the upper 16 bits the alternate function identifier`,
`__DT_BINDINGS_PINCTRL_RENESAS_RZA1_H`. Example value clusters are RZA1: `RZA1_PINS_PER_PORT=16`,
`RZA1_PINMUX=((b) * RZA1_PINS_PER_PORT + (p) | (f << 16))`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZA1_PINS_PER_PORT`, `RZA1_PINMUX`. Test signals include dt_binding_check coverage,
DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and peripheral bring-up using
representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/r7s72100-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/r7s9210-pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/r7s9210-pinctrl.h

Purpose: `r7s9210-pinctrl.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 25 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are RZA2 (3), PORT0 (1),
PORT1 (1), PORT2 (1), PORT3 (1), PORT4 (1), PORT5 (1), PORT6 (1), PORT7 (1), PORT8 (1).
Representative constants are `RZA2_PINS_PER_PORT`, `PORT0`, `PORT1`, `PORT2`, `PORT3`, `PORT4`,
`PORT5`, `PORT6`, `...`, `PORTE`, `PORTF`, `PORTG`, `PORTH`, `PORTJ`, `PORTK`, `PORTL`, `PORTM`.
Function-like helpers are `RZA2_PINMUX`, `RZA2_PIN`. Value shape: literal numeric range 0..20 across
22 macros; 3 alias or symbol-derived values; 2 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_RENESAS_RZA2_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Port names as labeled in the Hardware Manual`, `No I`, which is the intended lookup structure
for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 47 lines long. Notable source comments include `Defines macros and constants for Renesas
RZ/A2 pin controller pin muxing functions.`, `Port names as labeled in the Hardware Manual`, `No I`,
`Pins PM_0/1 are labeled JP_0/1 in HW manual`, `Create the pin index from its bank and position
numbers and store in the upper 16 bits the alternate function identifier`, `Convert a port and pin
label to its global pin index`. Example value clusters are RZA2: `RZA2_PINS_PER_PORT=8`,
`RZA2_PINMUX=((b) * RZA2_PINS_PER_PORT + (p) | (f << 16))`, `RZA2_PIN=((port) * RZA2_PINS_PER_PORT +
(pin))`; PORT0: `PORT0=0`; PORT1: `PORT1=1`; PORT2: `PORT2=2`; PORT3: `PORT3=3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZA2_PINS_PER_PORT`, `PORT0`, `PORT1`, `PORT2`, `PORT3`, `PORT4`, `PORT5`, `PORT6`.
Test signals include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe
logs, GPIO loopback, and peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/r7s9210-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/renesas,r9a09g047-pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/renesas,r9a09g047-pinctrl.h

Purpose: `renesas,r9a09g047-pinctrl.h` is a Devicetree binding header for a pin controller. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 24 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are RZG3E (24).
Representative constants are `RZG3E_P0`, `RZG3E_P1`, `RZG3E_P2`, `RZG3E_P3`, `RZG3E_P4`, `RZG3E_P5`,
`RZG3E_P6`, `RZG3E_P7`, `...`, `RZG3E_PF`, `RZG3E_PG`, `RZG3E_PH`, `RZG3E_PJ`, `RZG3E_PK`,
`RZG3E_PL`, `RZG3E_PM`, `RZG3E_PS`. Function-like helpers are `RZG3E_PORT_PINMUX`, `RZG3E_GPIO`.
Value shape: literal numeric range 0..28 across 22 macros; 2 alias or symbol-derived values; 2
function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_RENESAS_R9A09G047_PINCTRL_H__`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `RZG3E_Px = Offset address of PFC_P_mn - 0x20`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are `dt-bindings/pinctrl/rzg2l-pinctrl.h`. Integration points are pinctrl provider
drivers, board DTS files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 41 lines long. Notable source comments include `This header provides constants for
Renesas RZ/G3E family pinctrl bindings.`, `RZG3E_Px = Offset address of PFC_P_mn - 0x20`,
`__DT_BINDINGS_PINCTRL_RENESAS_R9A09G047_PINCTRL_H__`. Example value clusters are RZG3E:
`RZG3E_P0=0`, `RZG3E_P1=1`, `RZG3E_P2=2`, `RZG3E_P3=3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZG3E_P0`, `RZG3E_P1`, `RZG3E_P2`, `RZG3E_P3`, `RZG3E_P4`, `RZG3E_P5`, `RZG3E_P6`,
`RZG3E_P7`. Test signals include dt_binding_check coverage, DTS compile coverage for each SoC,
pinctrl probe logs, GPIO loopback, and peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/renesas,r9a09g047-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/renesas,r9a09g057-pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/renesas,r9a09g057-pinctrl.h

Purpose: `renesas,r9a09g057-pinctrl.h` is a Devicetree binding header for a pin controller. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 14 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are RZV2H (14).
Representative constants are `RZV2H_P0`, `RZV2H_P1`, `RZV2H_P2`, `RZV2H_P3`, `RZV2H_P4`, `RZV2H_P5`,
`RZV2H_P6`, `RZV2H_P7`, `RZV2H_P4`, `RZV2H_P5`, `RZV2H_P6`, `RZV2H_P7`, `RZV2H_P8`, `RZV2H_P9`,
`RZV2H_PA`, `RZV2H_PB`. Function-like helpers are `RZV2H_PORT_PINMUX`, `RZV2H_GPIO`. Value shape:
literal numeric range 0..11 across 12 macros; 2 alias or symbol-derived values; 2 function-like
packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_RENESAS_R9A09G057_PINCTRL_H__`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `RZV2H_Px = Offset address of PFC_P_mn - 0x20`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are `dt-bindings/pinctrl/rzg2l-pinctrl.h`. Integration points are pinctrl provider
drivers, board DTS files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 31 lines long. Notable source comments include `This header provides constants for
Renesas RZ/V2H family pinctrl bindings.`, `RZV2H_Px = Offset address of PFC_P_mn - 0x20`,
`__DT_BINDINGS_PINCTRL_RENESAS_R9A09G057_PINCTRL_H__`. Example value clusters are RZV2H:
`RZV2H_P0=0`, `RZV2H_P1=1`, `RZV2H_P2=2`, `RZV2H_P3=3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZV2H_P0`, `RZV2H_P1`, `RZV2H_P2`, `RZV2H_P3`, `RZV2H_P4`, `RZV2H_P5`, `RZV2H_P6`,
`RZV2H_P7`. Test signals include dt_binding_check coverage, DTS compile coverage for each SoC,
pinctrl probe logs, GPIO loopback, and peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/renesas,r9a09g057-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/renesas,r9a09g077-pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/renesas,r9a09g077-pinctrl.h

Purpose: `renesas,r9a09g077-pinctrl.h` is a Devicetree binding header for a pin controller. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are RZT2H (3). Representative
constants are `RZT2H_PINS_PER_PORT`, `RZT2H_PINS_PER_PORT`. Function-like helpers are
`RZT2H_PORT_PINMUX`, `RZT2H_GPIO`. Value shape: literal numeric range 8..8 across 1 macros; 2 alias
or symbol-derived values; 2 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_RENESAS_R9A09G077_PINCTRL_H__`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `Convert a port and pin label to its global pin index`, which is the intended
lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 22 lines long. Notable source comments include `This header provides constants for
Renesas RZ/T2H family pinctrl bindings.`, `Create the pin index from its bank and position numbers
and store in the upper 16 bits the alternate function identifier`, `Convert a port and pin label to
its global pin index`, `__DT_BINDINGS_PINCTRL_RENESAS_R9A09G077_PINCTRL_H__`. Example value clusters
are RZT2H: `RZT2H_PINS_PER_PORT=8`, `RZT2H_PORT_PINMUX=((b) * RZT2H_PINS_PER_PORT + (p) | ((f) <<
16))`, `RZT2H_GPIO=((port) * RZT2H_PINS_PER_PORT + (pin))`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZT2H_PINS_PER_PORT`, `RZT2H_PORT_PINMUX`, `RZT2H_GPIO`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/renesas,r9a09g077-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rockchip.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rockchip.h

Purpose: `rockchip.h` is a Devicetree binding header for a pin controller. It exports numeric C preprocessor
constants that DTS files and provider drivers share as the ABI for phandle cells, selector values,
and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 33 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are RK (32), RK_FUNC (1).
Representative constants are `RK_PA0`, `RK_PA1`, `RK_PA2`, `RK_PA3`, `RK_PA4`, `RK_PA5`, `RK_PA6`,
`RK_PA7`, `...`, `RK_PD1`, `RK_PD2`, `RK_PD3`, `RK_PD4`, `RK_PD5`, `RK_PD6`, `RK_PD7`,
`RK_FUNC_GPIO`. Function-like helpers are none. Value shape: literal numeric range 0..31 across 33
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_ROCKCHIP_PINCTRL_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RK group`, `RK_FUNC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 47 lines long. Notable source comments include `Header providing constants for Rockchip
pinctrl bindings.`. Example value clusters are RK: `RK_PA0=0`, `RK_PA1=1`, `RK_PA2=2`, `RK_PA3=3`;
RK_FUNC: `RK_FUNC_GPIO=0`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RK_PA0`, `RK_PA1`, `RK_PA2`, `RK_PA3`, `RK_PA4`, `RK_PA5`, `RK_PA6`, `RK_PA7`. Test
signals include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs,
GPIO loopback, and peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rockchip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzg2l-pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzg2l-pinctrl.h

Purpose: `rzg2l-pinctrl.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are RZG2L (3). Representative
constants are `RZG2L_PINS_PER_PORT`, `RZG2L_PINS_PER_PORT`. Function-like helpers are
`RZG2L_PORT_PINMUX`, `RZG2L_GPIO`. Value shape: literal numeric range 8..8 across 1 macros; 2 alias
or symbol-derived values; 2 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RZG2L_PINCTRL_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Convert a port and pin label to its global pin index`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 23 lines long. Notable source comments include `This header provides constants for
Renesas RZ/G2L family pinctrl bindings.`, `Create the pin index from its bank and position numbers
and store in the upper 16 bits the alternate function identifier`, `Convert a port and pin label to
its global pin index`, `__DT_BINDINGS_RZG2L_PINCTRL_H`. Example value clusters are RZG2L:
`RZG2L_PINS_PER_PORT=8`, `RZG2L_PORT_PINMUX=((b) * RZG2L_PINS_PER_PORT + (p) | ((f) << 16))`,
`RZG2L_GPIO=((port) * RZG2L_PINS_PER_PORT + (pin))`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZG2L_PINS_PER_PORT`, `RZG2L_PORT_PINMUX`, `RZG2L_GPIO`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzg2l-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzn1-pinctrl.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzn1-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzv2m-pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzv2m-pinctrl.h

Purpose: `rzv2m-pinctrl.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are RZV2M (3). Representative
constants are `RZV2M_PINS_PER_PORT`, `RZV2M_PINS_PER_PORT`. Function-like helpers are
`RZV2M_PORT_PINMUX`, `RZV2M_GPIO`. Value shape: literal numeric range 16..16 across 1 macros; 2
alias or symbol-derived values; 2 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RZV2M_PINCTRL_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Convert a port and pin label to its global pin index`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 23 lines long. Notable source comments include `This header provides constants for
Renesas RZ/V2M pinctrl bindings.`, `Create the pin index from its bank and position numbers and
store in the upper 16 bits the alternate function identifier`, `Convert a port and pin label to its
global pin index`, `__DT_BINDINGS_RZV2M_PINCTRL_H`. Example value clusters are RZV2M:
`RZV2M_PINS_PER_PORT=16`, `RZV2M_PORT_PINMUX=((b) * RZV2M_PINS_PER_PORT + (p) | ((f) << 16))`,
`RZV2M_GPIO=((port) * RZV2M_PINS_PER_PORT + (pin))`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `RZV2M_PINS_PER_PORT`, `RZV2M_PORT_PINMUX`, `RZV2M_GPIO`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/rzv2m-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sppctl-sp7021.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sppctl-sp7021.h

Purpose: `sppctl-sp7021.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 154 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are MUXF (122), GROP (32).
Representative constants are `MUXF_GPIO`, `MUXF_IOP`, `MUXF_L2SW_CLK_OUT`, `MUXF_L2SW_MAC_SMI_MDC`,
`MUXF_L2SW_LED_FLASH0`, `MUXF_L2SW_LED_FLASH1`, `MUXF_L2SW_LED_ON0`, `MUXF_L2SW_LED_ON1`, `...`,
`GROP_USB0_I2C`, `GROP_USB1_I2C`, `GROP_USB0_OTG`, `GROP_USB1_OTG`, `GROP_UPHY0_DEBUG`,
`GROP_UPHY1_DEBUG`, `GROP_UPHY0_EXT`, `GROP_PROBE_PORT`. Function-like helpers are none. Value
shape: literal numeric range 0..153 across 154 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_SPPCTL_SP7021_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `MUXF group`, `GROP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are `dt-bindings/pinctrl/sppctl.h`. Integration points are pinctrl provider drivers,
board DTS files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 179 lines long. Notable source comments include `Sunplus SP7021 dt-bindings Pinctrl
header file`, `Please don't change the order of the following defines. They are based on order of
'hardware' control register defined in MOON2 ~ MOON3 registers.`, `Please don't change the order of
the following defines. They are based on order of items in array 'sppctl_list_funcs' in Sunplus
pinctrl driver.`. Example value clusters are MUXF: `MUXF_GPIO=0`, `MUXF_IOP=1`,
`MUXF_L2SW_CLK_OUT=2`, `MUXF_L2SW_MAC_SMI_MDC=3`; GROP: `GROP_SPI_FLASH=122`,
`GROP_SPI_FLASH_4BIT=123`, `GROP_SPI_NAND=124`, `GROP_CARD0_EMMC=125`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `MUXF_GPIO`, `MUXF_IOP`, `MUXF_L2SW_CLK_OUT`, `MUXF_L2SW_MAC_SMI_MDC`,
`MUXF_L2SW_LED_FLASH0`, `MUXF_L2SW_LED_FLASH1`, `MUXF_L2SW_LED_ON0`, `MUXF_L2SW_LED_ON1`. Test
signals include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs,
GPIO loopback, and peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sppctl-sp7021.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sppctl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sppctl.h

Purpose: `sppctl.h` is a Devicetree binding header for a pin controller. It exports numeric C preprocessor
constants that DTS files and provider drivers share as the ABI for phandle cells, selector values,
and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are SPPCTL (9), IOP_G (2).
Representative constants are `IOP_G_MASTE`, `IOP_G_FIRST`, `SPPCTL_PCTL_G_PMUX`,
`SPPCTL_PCTL_G_GPIO`, `SPPCTL_PCTL_G_IOPP`, `SPPCTL_PCTL_L_OUT`, `SPPCTL_PCTL_L_OU1`,
`SPPCTL_PCTL_L_INV`, `SPPCTL_PCTL_G_PMUX`, `SPPCTL_PCTL_G_GPIO`, `SPPCTL_PCTL_G_IOPP`,
`SPPCTL_PCTL_L_OUT`, `SPPCTL_PCTL_L_OU1`, `SPPCTL_PCTL_L_INV`, `SPPCTL_PCTL_L_ONV`,
`SPPCTL_PCTL_L_ODR`. Function-like helpers are `SPPCTL_IOPAD`. Value shape: 11 alias or symbol-
derived values; 1 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_SPPCTL_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`SPPCTL group`, `IOP_G group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 31 lines long. Notable source comments include `Sunplus dt-bindings Pinctrl header
file`, `Output LOW`, `Output HIGH`, `Input Invert`, `Output Invert`, `Output Open Drain`. Example
value clusters are SPPCTL: `SPPCTL_PCTL_G_PMUX=(0x00 | IOP_G_MASTE)`,
`SPPCTL_PCTL_G_GPIO=(IOP_G_FIRST | IOP_G_MASTE)`, `SPPCTL_PCTL_G_IOPP=(IOP_G_FIRST | 0x00)`,
`SPPCTL_PCTL_L_OUT=(0x01 << 0) /* Output LOW */`; IOP_G: `IOP_G_MASTE=(0x01 << 0)`,
`IOP_G_FIRST=(0x01 << 1)`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `IOP_G_MASTE`, `IOP_G_FIRST`, `SPPCTL_PCTL_G_PMUX`, `SPPCTL_PCTL_G_GPIO`,
`SPPCTL_PCTL_G_IOPP`, `SPPCTL_PCTL_L_OUT`, `SPPCTL_PCTL_L_OU1`, `SPPCTL_PCTL_L_INV`. Test signals
include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO
loopback, and peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sppctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/starfive,jh7110-pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/starfive,jh7110-pinctrl.h

Purpose: `starfive,jh7110-pinctrl.h` is a Devicetree binding header for a pin controller. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 120 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are PAD_GMAC1 (14),
PAD_GMAC0 (14), PAD_SD0 (11), PAD_QSPI (6), GPOUT (2), GPOEN (2), PAD_GPIO0 (1), PAD_GPIO1 (1),
PAD_GPIO2 (1), PAD_GPIO3 (1). Representative constants are `PAD_GPIO0`, `PAD_GPIO1`, `PAD_GPIO2`,
`PAD_GPIO3`, `PAD_GPIO4`, `PAD_GPIO5`, `PAD_GPIO6`, `PAD_GPIO7`, `...`, `PAD_GMAC0_TXD3`,
`PAD_GMAC0_TXEN`, `PAD_GMAC0_TXC`, `GPOUT_LOW`, `GPOUT_HIGH`, `GPOEN_ENABLE`, `GPOEN_DISABLE`,
`GPI_NONE`. Function-like helpers are none. Value shape: literal numeric range 0..255 across 120
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_STARFIVE_JH7110_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `sys_iomux pins`, `aon_iomux pins`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 137 lines long. Notable source comments include `sys_iomux pins`, `aon_iomux pins`.
Example value clusters are PAD_GMAC1: `PAD_GMAC1_MDC=75`, `PAD_GMAC1_MDIO=76`, `PAD_GMAC1_RXD0=77`,
`PAD_GMAC1_RXD1=78`; PAD_GMAC0: `PAD_GMAC0_MDC=6`, `PAD_GMAC0_MDIO=7`, `PAD_GMAC0_RXD0=8`,
`PAD_GMAC0_RXD1=9`; PAD_SD0: `PAD_SD0_CLK=64`, `PAD_SD0_CMD=65`, `PAD_SD0_DATA0=66`,
`PAD_SD0_DATA1=67`; PAD_QSPI: `PAD_QSPI_SCLK=89`, `PAD_QSPI_CS0=90`, `PAD_QSPI_DATA0=91`,
`PAD_QSPI_DATA1=92`; GPOUT: `GPOUT_LOW=0`, `GPOUT_HIGH=1`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `PAD_GPIO0`, `PAD_GPIO1`, `PAD_GPIO2`, `PAD_GPIO3`, `PAD_GPIO4`, `PAD_GPIO5`,
`PAD_GPIO6`, `PAD_GPIO7`. Test signals include dt_binding_check coverage, DTS compile coverage for
each SoC, pinctrl probe logs, GPIO loopback, and peripheral bring-up using representative mux
groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/starfive,jh7110-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/stm32-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/stm32-pinfunc.h

Purpose: `stm32-pinfunc.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 28 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are STM32MP (7), GPIO (1),
AF0 (1), AF1 (1), AF2 (1), AF3 (1), AF4 (1), AF5 (1), AF6 (1), AF7 (1). Representative constants are
`GPIO`, `AF0`, `AF1`, `AF2`, `AF3`, `AF4`, `AF5`, `AF6`, `...`, `RSVD`, `STM32MP_PKG_AA`,
`STM32MP_PKG_AB`, `STM32MP_PKG_AC`, `STM32MP_PKG_AD`, `STM32MP_PKG_AI`, `STM32MP_PKG_AK`,
`STM32MP_PKG_AL`. Function-like helpers are `PIN_NO`, `STM32_PINMUX`. Value shape: literal numeric
range 0..2048 across 26 macros; 2 alias or symbol-derived values; 2 function-like packing helpers.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_STM32_PINFUNC_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`define PIN modes`, `define Pins number`, `package information`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 46 lines long. Notable source comments include `define PIN modes`, `define Pins number`,
`package information`, `_DT_BINDINGS_STM32_PINFUNC_H`. Example value clusters are STM32MP:
`STM32MP_PKG_AA=0x1`, `STM32MP_PKG_AB=0x2`, `STM32MP_PKG_AC=0x4`, `STM32MP_PKG_AD=0x8`; GPIO:
`GPIO=0x0`; AF0: `AF0=0x1`; AF1: `AF1=0x2`; AF2: `AF2=0x3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `GPIO`, `AF0`, `AF1`, `AF2`, `AF3`, `AF4`, `AF5`, `AF6`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/stm32-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sun4i-a10.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sun4i-a10.h

Purpose: `sun4i-a10.h` is a Devicetree binding header for a pin controller. It exports numeric C preprocessor
constants that DTS files and provider drivers share as the ABI for phandle cells, selector values,
and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are SUN4I (7). Representative
constants are `SUN4I_PINCTRL_10_MA`, `SUN4I_PINCTRL_20_MA`, `SUN4I_PINCTRL_30_MA`,
`SUN4I_PINCTRL_40_MA`, `SUN4I_PINCTRL_NO_PULL`, `SUN4I_PINCTRL_PULL_UP`, `SUN4I_PINCTRL_PULL_DOWN`,
`SUN4I_PINCTRL_10_MA`, `SUN4I_PINCTRL_20_MA`, `SUN4I_PINCTRL_30_MA`, `SUN4I_PINCTRL_40_MA`,
`SUN4I_PINCTRL_NO_PULL`, `SUN4I_PINCTRL_PULL_UP`, `SUN4I_PINCTRL_PULL_DOWN`. Function-like helpers
are none. Value shape: literal numeric range 0..3 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_SUN4I_A10_H_`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `SUN4I group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 62 lines long. Notable source comments include `Maxime Ripard <maxime.ripard@free-
electrons.com> This file is dual-licensed: you can use it either under the terms of the GPL or the
X11 license, at your option. Note that this dual licensing only applies to this file, and not this
project as a whole. a) This file is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version. This file is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with this file; if
not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301
USA Or, alternatively, b) Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions: The above copyright notice and
this permission notice shall be included in all copies or substantial portions of the Software. THE
SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.`,
`__DT_BINDINGS_PINCTRL_SUN4I_A10_H_`. Example value clusters are SUN4I: `SUN4I_PINCTRL_10_MA=0`,
`SUN4I_PINCTRL_20_MA=1`, `SUN4I_PINCTRL_30_MA=2`, `SUN4I_PINCTRL_40_MA=3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `SUN4I_PINCTRL_10_MA`, `SUN4I_PINCTRL_20_MA`, `SUN4I_PINCTRL_30_MA`,
`SUN4I_PINCTRL_40_MA`, `SUN4I_PINCTRL_NO_PULL`, `SUN4I_PINCTRL_PULL_UP`, `SUN4I_PINCTRL_PULL_DOWN`.
Test signals include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe
logs, GPIO loopback, and peripheral bring-up using representative mux groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sun4i-a10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pmu/exynos_ppmu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pmu/exynos_ppmu.h

Purpose: `exynos_ppmu.h` is a Devicetree binding header for a PMU/PPMU provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 12 `#define`s covering PMU/PPMU event and counter
selector constants. The main macro families are PPMU (12). Representative constants are
`PPMU_RO_BUSY_CYCLE_CNT`, `PPMU_WO_BUSY_CYCLE_CNT`, `PPMU_RW_BUSY_CYCLE_CNT`, `PPMU_RO_REQUEST_CNT`,
`PPMU_WO_REQUEST_CNT`, `PPMU_RO_DATA_CNT`, `PPMU_WO_DATA_CNT`, `PPMU_RO_LATENCY`,
`PPMU_WO_REQUEST_CNT`, `PPMU_RO_DATA_CNT`, `PPMU_WO_DATA_CNT`, `PPMU_RO_LATENCY`, `PPMU_WO_LATENCY`,
`PPMU_V2_RO_DATA_CNT`, `PPMU_V2_WO_DATA_CNT`, `PPMU_V2_EVT3_RW_DATA_CNT`. Function-like helpers are
none. Value shape: literal numeric range 0..34 across 12 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PMU_EXYNOS_PPMU_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PPMU group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are PPMU/PMU drivers and DTS nodes
describing monitored bus or memory interfaces.

Local source signals: The file is 25 lines long. Notable source comments include `Samsung Exynos PPMU event types for
counting in regs`. Example value clusters are PPMU: `PPMU_RO_BUSY_CYCLE_CNT=0x0`,
`PPMU_WO_BUSY_CYCLE_CNT=0x1`, `PPMU_RW_BUSY_CYCLE_CNT=0x2`, `PPMU_RO_REQUEST_CNT=0x3`.

Risks and test signals: Primary risks are event selector drift can make performance counters sample the wrong bus endpoint.
Pay special attention to exported symbols such as `PPMU_RO_BUSY_CYCLE_CNT`,
`PPMU_WO_BUSY_CYCLE_CNT`, `PPMU_RW_BUSY_CYCLE_CNT`, `PPMU_RO_REQUEST_CNT`, `PPMU_WO_REQUEST_CNT`,
`PPMU_RO_DATA_CNT`, `PPMU_WO_DATA_CNT`, `PPMU_RO_LATENCY`. Test signals include PPMU probe, event
selection smoke tests, and DTS validation for all monitored channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pmu/exynos_ppmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun20i-d1-ppu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun20i-d1-ppu.h

Purpose: `allwinner,sun20i-d1-ppu.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_CPU (1), PD_VE (1), PD_DSP (1).
Representative constants are `PD_CPU`, `PD_VE`, `PD_DSP`, `PD_CPU`, `PD_VE`, `PD_DSP`. Function-like
helpers are none. Value shape: literal numeric range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_SUN20I_D1_PPU_H_`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PD_CPU group`, `PD_VE group`, `PD_DSP group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 10 lines long. Notable source comments include `_DT_BINDINGS_POWER_SUN20I_D1_PPU_H_`.
Example value clusters are PD_CPU: `PD_CPU=0`; PD_VE: `PD_VE=1`; PD_DSP: `PD_DSP=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_CPU`, `PD_VE`, `PD_DSP`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun20i-d1-ppu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun55i-a523-pck-600.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun55i-a523-pck-600.h

Purpose: `allwinner,sun55i-a523-pck-600.h` is a Devicetree binding header for a power-domain provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_VE (1), PD_GPU (1), PD_VI (1),
PD_VO0 (1), PD_VO1 (1), PD_DE (1), PD_NAND (1), PD_PCIE (1). Representative constants are `PD_VE`,
`PD_GPU`, `PD_VI`, `PD_VO0`, `PD_VO1`, `PD_DE`, `PD_NAND`, `PD_PCIE`, `PD_VE`, `PD_GPU`, `PD_VI`,
`PD_VO0`, `PD_VO1`, `PD_DE`, `PD_NAND`, `PD_PCIE`. Function-like helpers are none. Value shape:
literal numeric range 0..7 across 8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_SUN55I_A523_PCK600_H_`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `PD_VE group`, `PD_GPU group`, `PD_VI group`, `PD_VO0 group`, `PD_VO1 group`, `PD_DE
group`, `PD_NAND group`, `PD_PCIE group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 15 lines long. Notable source comments include
`_DT_BINDINGS_POWER_SUN55I_A523_PCK600_H_`. Example value clusters are PD_VE: `PD_VE=0`; PD_GPU:
`PD_GPU=1`; PD_VI: `PD_VI=2`; PD_VO0: `PD_VO0=3`; PD_VO1: `PD_VO1=4`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_VE`, `PD_GPU`, `PD_VI`, `PD_VO0`, `PD_VO1`, `PD_DE`, `PD_NAND`, `PD_PCIE`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun55i-a523-pck-600.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun55i-a523-ppu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun55i-a523-ppu.h

Purpose: `allwinner,sun55i-a523-ppu.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_DSP (1), PD_NPU (1), PD_AUDIO
(1), PD_SRAM (1), PD_RISCV (1). Representative constants are `PD_DSP`, `PD_NPU`, `PD_AUDIO`,
`PD_SRAM`, `PD_RISCV`, `PD_DSP`, `PD_NPU`, `PD_AUDIO`, `PD_SRAM`, `PD_RISCV`. Function-like helpers
are none. Value shape: literal numeric range 0..4 across 5 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_SUN55I_A523_PPU_H_`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PD_DSP group`, `PD_NPU group`, `PD_AUDIO group`, `PD_SRAM group`, `PD_RISCV group`, which is
the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 12 lines long. Notable source comments include `_DT_BINDINGS_POWER_SUN55I_A523_PPU_H_`.
Example value clusters are PD_DSP: `PD_DSP=0`; PD_NPU: `PD_NPU=1`; PD_AUDIO: `PD_AUDIO=2`; PD_SRAM:
`PD_SRAM=3`; PD_RISCV: `PD_RISCV=4`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_DSP`, `PD_NPU`, `PD_AUDIO`, `PD_SRAM`, `PD_RISCV`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun55i-a523-ppu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun60i-a733-pck-600.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun60i-a733-pck-600.h

Purpose: `allwinner,sun60i-a733-pck-600.h` is a Devicetree binding header for a power-domain provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_VE (2), PD_GPU (2), PD_VI (1),
PD_DE (1), PD_NPU (1), PD_PCIE (1), PD_USB2 (1), PD_VO (1), PD_VO1 (1). Representative constants are
`PD_VI`, `PD_DE_SYS`, `PD_VE_DEC`, `PD_VE_ENC`, `PD_NPU`, `PD_GPU_TOP`, `PD_GPU_CORE`, `PD_PCIE`,
`PD_VE_ENC`, `PD_NPU`, `PD_GPU_TOP`, `PD_GPU_CORE`, `PD_PCIE`, `PD_USB2`, `PD_VO`, `PD_VO1`.
Function-like helpers are none. Value shape: literal numeric range 0..10 across 11 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_SUN60I_A733_PCK600_H_`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `PD_VE group`, `PD_GPU group`, `PD_VI group`, `PD_DE group`, `PD_NPU group`, `PD_PCIE
group`, `PD_USB2 group`, `PD_VO group`, `PD_VO1 group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 18 lines long. Notable source comments include
`_DT_BINDINGS_POWER_SUN60I_A733_PCK600_H_`. Example value clusters are PD_VE: `PD_VE_DEC=2`,
`PD_VE_ENC=3`; PD_GPU: `PD_GPU_TOP=5`, `PD_GPU_CORE=6`; PD_VI: `PD_VI=0`; PD_DE: `PD_DE_SYS=1`;
PD_NPU: `PD_NPU=4`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_VI`, `PD_DE_SYS`, `PD_VE_DEC`, `PD_VE_ENC`, `PD_NPU`, `PD_GPU_TOP`, `PD_GPU_CORE`, `PD_PCIE`.
Test signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun60i-a733-pck-600.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun8i-v853-ppu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun8i-v853-ppu.h

Purpose: `allwinner,sun8i-v853-ppu.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_RISCV (1), PD_NPU (1), PD_VE
(1). Representative constants are `PD_RISCV`, `PD_NPU`, `PD_VE`, `PD_RISCV`, `PD_NPU`, `PD_VE`.
Function-like helpers are none. Value shape: literal numeric range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_SUN8I_V853_PPU_H_`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PD_RISCV group`, `PD_NPU group`, `PD_VE group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 10 lines long. Notable source comments include none. Example value clusters are
PD_RISCV: `PD_RISCV=0`; PD_NPU: `PD_NPU=1`; PD_VE: `PD_VE=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_RISCV`, `PD_NPU`, `PD_VE`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun8i-v853-ppu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,a4-pwrc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,a4-pwrc.h

Purpose: `amlogic,a4-pwrc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 12 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (12). Representative constants
are `PWRC_A4_AUDIO_ID`, `PWRC_A4_SDIOA_ID`, `PWRC_A4_EMMC_ID`, `PWRC_A4_USB_COMB_ID`,
`PWRC_A4_ETH_ID`, `PWRC_A4_VOUT_ID`, `PWRC_A4_AUDIO_PDM_ID`, `PWRC_A4_DMC_ID`, `PWRC_A4_ETH_ID`,
`PWRC_A4_VOUT_ID`, `PWRC_A4_AUDIO_PDM_ID`, `PWRC_A4_DMC_ID`, `PWRC_A4_SYS_WRAP_ID`,
`PWRC_A4_AO_I2C_S_ID`, `PWRC_A4_AO_UART_ID`, `PWRC_A4_AO_IR_ID`. Function-like helpers are none.
Value shape: literal numeric range 0..11 across 12 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_A4_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 21 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_A4_AUDIO_ID=0`, `PWRC_A4_SDIOA_ID=1`, `PWRC_A4_EMMC_ID=2`, `PWRC_A4_USB_COMB_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_A4_AUDIO_ID`, `PWRC_A4_SDIOA_ID`, `PWRC_A4_EMMC_ID`, `PWRC_A4_USB_COMB_ID`, `PWRC_A4_ETH_ID`,
`PWRC_A4_VOUT_ID`, `PWRC_A4_AUDIO_PDM_ID`, `PWRC_A4_DMC_ID`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,a4-pwrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,a5-pwrc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,a5-pwrc.h

Purpose: `amlogic,a5-pwrc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (11). Representative constants
are `PWRC_A5_NNA_ID`, `PWRC_A5_AUDIO_ID`, `PWRC_A5_SDIOA_ID`, `PWRC_A5_EMMC_ID`,
`PWRC_A5_USB_COMB_ID`, `PWRC_A5_ETH_ID`, `PWRC_A5_RSA_ID`, `PWRC_A5_AUDIO_PDM_ID`,
`PWRC_A5_EMMC_ID`, `PWRC_A5_USB_COMB_ID`, `PWRC_A5_ETH_ID`, `PWRC_A5_RSA_ID`,
`PWRC_A5_AUDIO_PDM_ID`, `PWRC_A5_DMC_ID`, `PWRC_A5_SYS_WRAP_ID`, `PWRC_A5_DSPA_ID`. Function-like
helpers are none. Value shape: literal numeric range 0..10 across 11 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_A5_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 21 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_A5_NNA_ID=0`, `PWRC_A5_AUDIO_ID=1`, `PWRC_A5_SDIOA_ID=2`, `PWRC_A5_EMMC_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_A5_NNA_ID`, `PWRC_A5_AUDIO_ID`, `PWRC_A5_SDIOA_ID`, `PWRC_A5_EMMC_ID`, `PWRC_A5_USB_COMB_ID`,
`PWRC_A5_ETH_ID`, `PWRC_A5_RSA_ID`, `PWRC_A5_AUDIO_PDM_ID`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,a5-pwrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,c3-pwrc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,c3-pwrc.h

Purpose: `amlogic,c3-pwrc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 15 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (15). Representative constants
are `PWRC_C3_NNA_ID`, `PWRC_C3_AUDIO_ID`, `PWRC_C3_RESV_SEC_ID`, `PWRC_C3_SDIOA_ID`,
`PWRC_C3_EMMC_ID`, `PWRC_C3_USB_COMB_ID`, `PWRC_C3_SDCARD_ID`, `PWRC_C3_ETH_ID`, `PWRC_C3_ETH_ID`,
`PWRC_C3_RESV0_ID`, `PWRC_C3_GE2D_ID`, `PWRC_C3_CVE_ID`, `PWRC_C3_GDC_WRAP_ID`,
`PWRC_C3_ISP_TOP_ID`, `PWRC_C3_MIPI_ISP_WRAP_ID`, `PWRC_C3_VCODEC_ID`. Function-like helpers are
none. Value shape: literal numeric range 0..14 across 15 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_C3_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 25 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_C3_NNA_ID=0`, `PWRC_C3_AUDIO_ID=1`, `PWRC_C3_RESV_SEC_ID=2`, `PWRC_C3_SDIOA_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_C3_NNA_ID`, `PWRC_C3_AUDIO_ID`, `PWRC_C3_RESV_SEC_ID`, `PWRC_C3_SDIOA_ID`, `PWRC_C3_EMMC_ID`,
`PWRC_C3_USB_COMB_ID`, `PWRC_C3_SDCARD_ID`, `PWRC_C3_ETH_ID`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,c3-pwrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,s6-pwrc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,s6-pwrc.h

Purpose: `amlogic,s6-pwrc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 20 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (20). Representative constants
are `PWRC_S6_DSPA_ID`, `PWRC_S6_DOS_HEVC_ID`, `PWRC_S6_DOS_VDEC_ID`, `PWRC_S6_VPU_HDMI_ID`,
`PWRC_S6_U2DRD_ID`, `PWRC_S6_U3DRD_ID`, `PWRC_S6_SD_EMMC_C_ID`, `PWRC_S6_GE2D_ID`, `...`,
`PWRC_S6_SD_EMMC_A_ID`, `PWRC_S6_SD_EMMC_B_ID`, `PWRC_S6_ETH_ID`, `PWRC_S6_PCIE_ID`,
`PWRC_S6_NNA_4T_ID`, `PWRC_S6_AUDIO_ID`, `PWRC_S6_AUCPU_ID`, `PWRC_S6_ADAPT_ID`. Function-like
helpers are none. Value shape: literal numeric range 0..19 across 20 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_S6_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 29 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_S6_DSPA_ID=0`, `PWRC_S6_DOS_HEVC_ID=1`, `PWRC_S6_DOS_VDEC_ID=2`, `PWRC_S6_VPU_HDMI_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_S6_DSPA_ID`, `PWRC_S6_DOS_HEVC_ID`, `PWRC_S6_DOS_VDEC_ID`, `PWRC_S6_VPU_HDMI_ID`,
`PWRC_S6_U2DRD_ID`, `PWRC_S6_U3DRD_ID`, `PWRC_S6_SD_EMMC_C_ID`, `PWRC_S6_GE2D_ID`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,s6-pwrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,s7-pwrc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,s7-pwrc.h

Purpose: `amlogic,s7-pwrc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (11). Representative constants
are `PWRC_S7_DOS_HEVC_ID`, `PWRC_S7_DOS_VDEC_ID`, `PWRC_S7_VPU_HDMI_ID`, `PWRC_S7_USB_COMB_ID`,
`PWRC_S7_SD_EMMC_C_ID`, `PWRC_S7_GE2D_ID`, `PWRC_S7_SD_EMMC_A_ID`, `PWRC_S7_SD_EMMC_B_ID`,
`PWRC_S7_USB_COMB_ID`, `PWRC_S7_SD_EMMC_C_ID`, `PWRC_S7_GE2D_ID`, `PWRC_S7_SD_EMMC_A_ID`,
`PWRC_S7_SD_EMMC_B_ID`, `PWRC_S7_ETH_ID`, `PWRC_S7_AUCPU_ID`, `PWRC_S7_AUDIO_ID`. Function-like
helpers are none. Value shape: literal numeric range 0..10 across 11 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_S7_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 20 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_S7_DOS_HEVC_ID=0`, `PWRC_S7_DOS_VDEC_ID=1`, `PWRC_S7_VPU_HDMI_ID=2`, `PWRC_S7_USB_COMB_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_S7_DOS_HEVC_ID`, `PWRC_S7_DOS_VDEC_ID`, `PWRC_S7_VPU_HDMI_ID`, `PWRC_S7_USB_COMB_ID`,
`PWRC_S7_SD_EMMC_C_ID`, `PWRC_S7_GE2D_ID`, `PWRC_S7_SD_EMMC_A_ID`, `PWRC_S7_SD_EMMC_B_ID`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,s7-pwrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,s7d-pwrc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,s7d-pwrc.h

Purpose: `amlogic,s7d-pwrc.h` is a Devicetree binding header for a power-domain provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 18 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (18). Representative constants
are `PWRC_S7D_DOS_HCODEC_ID`, `PWRC_S7D_DOS_HEVC_ID`, `PWRC_S7D_DOS_VDEC_ID`,
`PWRC_S7D_VPU_HDMI_ID`, `PWRC_S7D_USB_U2DRD_ID`, `PWRC_S7D_USB_U2H_ID`, `PWRC_S7D_SSD_EMMC_C_ID`,
`PWRC_S7D_GE2D_ID`, `...`, `PWRC_S7D_EMMC_B_ID`, `PWRC_S7D_ETH_ID`, `PWRC_S7D_AUCPU_ID`,
`PWRC_S7D_AUDIO_ID`, `PWRC_S7D_SRAMA_ID`, `PWRC_S7D_DMC0_ID`, `PWRC_S7D_DMC1_ID`, `PWRC_S7D_DDR_ID`.
Function-like helpers are none. Value shape: literal numeric range 0..17 across 18 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_S7D_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 27 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_S7D_DOS_HCODEC_ID=0`, `PWRC_S7D_DOS_HEVC_ID=1`, `PWRC_S7D_DOS_VDEC_ID=2`,
`PWRC_S7D_VPU_HDMI_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_S7D_DOS_HCODEC_ID`, `PWRC_S7D_DOS_HEVC_ID`, `PWRC_S7D_DOS_VDEC_ID`, `PWRC_S7D_VPU_HDMI_ID`,
`PWRC_S7D_USB_U2DRD_ID`, `PWRC_S7D_USB_U2H_ID`, `PWRC_S7D_SSD_EMMC_C_ID`, `PWRC_S7D_GE2D_ID`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,s7d-pwrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,t7-pwrc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,t7-pwrc.h

Purpose: `amlogic,t7-pwrc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 53 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (53). Representative constants
are `PWRC_T7_DSPA_ID`, `PWRC_T7_DSPB_ID`, `PWRC_T7_DOS_HCODEC_ID`, `PWRC_T7_DOS_HEVC_ID`,
`PWRC_T7_DOS_VDEC_ID`, `PWRC_T7_DOS_WAVE_ID`, `PWRC_T7_VPU_HDMI_ID`, `PWRC_T7_USB_COMB_ID`, `...`,
`PWRC_T7_SPICC2_ID`, `PWRC_T7_SPICC3_ID`, `PWRC_T7_SPICC4_ID`, `PWRC_T7_SPICC5_ID`,
`PWRC_T7_EDP0_ID`, `PWRC_T7_EDP1_ID`, `PWRC_T7_MIPI_DSI1_ID`, `PWRC_T7_AUDIO_ID`. Function-like
helpers are none. Value shape: literal numeric range 0..51 across 53 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_T7_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 63 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_T7_DSPA_ID=0`, `PWRC_T7_DSPB_ID=1`, `PWRC_T7_DOS_HCODEC_ID=2`, `PWRC_T7_DOS_HEVC_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_T7_DSPA_ID`, `PWRC_T7_DSPB_ID`, `PWRC_T7_DOS_HCODEC_ID`, `PWRC_T7_DOS_HEVC_ID`,
`PWRC_T7_DOS_VDEC_ID`, `PWRC_T7_DOS_WAVE_ID`, `PWRC_T7_VPU_HDMI_ID`, `PWRC_T7_USB_COMB_ID`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,t7-pwrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/fsl,imx93-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/fsl,imx93-power.h

Purpose: `fsl,imx93-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX93 (5). Representative constants
are `IMX93_MEDIABLK_PD_MIPI_DSI`, `IMX93_MEDIABLK_PD_MIPI_CSI`, `IMX93_MEDIABLK_PD_PXP`,
`IMX93_MEDIABLK_PD_LCDIF`, `IMX93_MEDIABLK_PD_ISI`, `IMX93_MEDIABLK_PD_MIPI_DSI`,
`IMX93_MEDIABLK_PD_MIPI_CSI`, `IMX93_MEDIABLK_PD_PXP`, `IMX93_MEDIABLK_PD_LCDIF`,
`IMX93_MEDIABLK_PD_ISI`. Function-like helpers are none. Value shape: literal numeric range 0..4
across 5 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX93_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX93 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 15 lines long. Notable source comments include none. Example value clusters are IMX93:
`IMX93_MEDIABLK_PD_MIPI_DSI=0`, `IMX93_MEDIABLK_PD_MIPI_CSI=1`, `IMX93_MEDIABLK_PD_PXP=2`,
`IMX93_MEDIABLK_PD_LCDIF=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX93_MEDIABLK_PD_MIPI_DSI`, `IMX93_MEDIABLK_PD_MIPI_CSI`, `IMX93_MEDIABLK_PD_PXP`,
`IMX93_MEDIABLK_PD_LCDIF`, `IMX93_MEDIABLK_PD_ISI`. Test signals include dt_binding_check, boot-time
genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/fsl,imx93-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx7-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx7-power.h

Purpose: `imx7-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX7 (3). Representative constants
are `IMX7_POWER_DOMAIN_MIPI_PHY`, `IMX7_POWER_DOMAIN_PCIE_PHY`, `IMX7_POWER_DOMAIN_USB_HSIC_PHY`,
`IMX7_POWER_DOMAIN_MIPI_PHY`, `IMX7_POWER_DOMAIN_PCIE_PHY`, `IMX7_POWER_DOMAIN_USB_HSIC_PHY`.
Function-like helpers are none. Value shape: literal numeric range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX7_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are `IMX7
group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 13 lines long. Notable source comments include none. Example value clusters are IMX7:
`IMX7_POWER_DOMAIN_MIPI_PHY=0`, `IMX7_POWER_DOMAIN_PCIE_PHY=1`, `IMX7_POWER_DOMAIN_USB_HSIC_PHY=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX7_POWER_DOMAIN_MIPI_PHY`, `IMX7_POWER_DOMAIN_PCIE_PHY`, `IMX7_POWER_DOMAIN_USB_HSIC_PHY`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx7-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mm-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mm-power.h

Purpose: `imx8mm-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 19 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX8MM (19). Representative
constants are `IMX8MM_POWER_DOMAIN_HSIOMIX`, `IMX8MM_POWER_DOMAIN_PCIE`, `IMX8MM_POWER_DOMAIN_OTG1`,
`IMX8MM_POWER_DOMAIN_OTG2`, `IMX8MM_POWER_DOMAIN_GPUMIX`, `IMX8MM_POWER_DOMAIN_GPU`,
`IMX8MM_POWER_DOMAIN_VPUMIX`, `IMX8MM_POWER_DOMAIN_VPUG1`, `...`, `IMX8MM_POWER_DOMAIN_MIPI`,
`IMX8MM_VPUBLK_PD_G1`, `IMX8MM_VPUBLK_PD_G2`, `IMX8MM_VPUBLK_PD_H1`, `IMX8MM_DISPBLK_PD_CSI_BRIDGE`,
`IMX8MM_DISPBLK_PD_LCDIF`, `IMX8MM_DISPBLK_PD_MIPI_DSI`, `IMX8MM_DISPBLK_PD_MIPI_CSI`. Function-like
helpers are none. Value shape: literal numeric range 0..11 across 19 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX8MM_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX8MM group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 31 lines long. Notable source comments include none. Example value clusters are IMX8MM:
`IMX8MM_POWER_DOMAIN_HSIOMIX=0`, `IMX8MM_POWER_DOMAIN_PCIE=1`, `IMX8MM_POWER_DOMAIN_OTG1=2`,
`IMX8MM_POWER_DOMAIN_OTG2=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX8MM_POWER_DOMAIN_HSIOMIX`, `IMX8MM_POWER_DOMAIN_PCIE`, `IMX8MM_POWER_DOMAIN_OTG1`,
`IMX8MM_POWER_DOMAIN_OTG2`, `IMX8MM_POWER_DOMAIN_GPUMIX`, `IMX8MM_POWER_DOMAIN_GPU`,
`IMX8MM_POWER_DOMAIN_VPUMIX`, `IMX8MM_POWER_DOMAIN_VPUG1`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mm-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mn-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mn-power.h

Purpose: `imx8mn-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX8MN (9). Representative
constants are `IMX8MN_POWER_DOMAIN_HSIOMIX`, `IMX8MN_POWER_DOMAIN_OTG1`,
`IMX8MN_POWER_DOMAIN_GPUMIX`, `IMX8MN_POWER_DOMAIN_DISPMIX`, `IMX8MN_POWER_DOMAIN_MIPI`,
`IMX8MN_DISPBLK_PD_MIPI_DSI`, `IMX8MN_DISPBLK_PD_MIPI_CSI`, `IMX8MN_DISPBLK_PD_LCDIF`,
`IMX8MN_POWER_DOMAIN_OTG1`, `IMX8MN_POWER_DOMAIN_GPUMIX`, `IMX8MN_POWER_DOMAIN_DISPMIX`,
`IMX8MN_POWER_DOMAIN_MIPI`, `IMX8MN_DISPBLK_PD_MIPI_DSI`, `IMX8MN_DISPBLK_PD_MIPI_CSI`,
`IMX8MN_DISPBLK_PD_LCDIF`, `IMX8MN_DISPBLK_PD_ISI`. Function-like helpers are none. Value shape:
literal numeric range 0..4 across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX8MN_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX8MN group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 20 lines long. Notable source comments include none. Example value clusters are IMX8MN:
`IMX8MN_POWER_DOMAIN_HSIOMIX=0`, `IMX8MN_POWER_DOMAIN_OTG1=1`, `IMX8MN_POWER_DOMAIN_GPUMIX=2`,
`IMX8MN_POWER_DOMAIN_DISPMIX=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX8MN_POWER_DOMAIN_HSIOMIX`, `IMX8MN_POWER_DOMAIN_OTG1`, `IMX8MN_POWER_DOMAIN_GPUMIX`,
`IMX8MN_POWER_DOMAIN_DISPMIX`, `IMX8MN_POWER_DOMAIN_MIPI`, `IMX8MN_DISPBLK_PD_MIPI_DSI`,
`IMX8MN_DISPBLK_PD_MIPI_CSI`, `IMX8MN_DISPBLK_PD_LCDIF`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mn-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mp-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mp-power.h

Purpose: `imx8mp-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 45 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX8MP (45). Representative
constants are `IMX8MP_POWER_DOMAIN_MIPI_PHY1`, `IMX8MP_POWER_DOMAIN_PCIE_PHY`,
`IMX8MP_POWER_DOMAIN_USB1_PHY`, `IMX8MP_POWER_DOMAIN_USB2_PHY`, `IMX8MP_POWER_DOMAIN_MLMIX`,
`IMX8MP_POWER_DOMAIN_AUDIOMIX`, `IMX8MP_POWER_DOMAIN_GPU2D`, `IMX8MP_POWER_DOMAIN_GPUMIX`, `...`,
`IMX8MP_HDMIBLK_PD_TRNG`, `IMX8MP_HDMIBLK_PD_HDMI_TX`, `IMX8MP_HDMIBLK_PD_HDMI_TX_PHY`,
`IMX8MP_HDMIBLK_PD_HDCP`, `IMX8MP_HDMIBLK_PD_HRV`, `IMX8MP_VPUBLK_PD_G1`, `IMX8MP_VPUBLK_PD_G2`,
`IMX8MP_VPUBLK_PD_VC8000E`. Function-like helpers are none. Value shape: literal numeric range 0..18
across 45 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX8MP_POWER_DOMAIN_POWER_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `IMX8MP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 59 lines long. Notable source comments include none. Example value clusters are IMX8MP:
`IMX8MP_POWER_DOMAIN_MIPI_PHY1=0`, `IMX8MP_POWER_DOMAIN_PCIE_PHY=1`,
`IMX8MP_POWER_DOMAIN_USB1_PHY=2`, `IMX8MP_POWER_DOMAIN_USB2_PHY=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX8MP_POWER_DOMAIN_MIPI_PHY1`, `IMX8MP_POWER_DOMAIN_PCIE_PHY`, `IMX8MP_POWER_DOMAIN_USB1_PHY`,
`IMX8MP_POWER_DOMAIN_USB2_PHY`, `IMX8MP_POWER_DOMAIN_MLMIX`, `IMX8MP_POWER_DOMAIN_AUDIOMIX`,
`IMX8MP_POWER_DOMAIN_GPU2D`, `IMX8MP_POWER_DOMAIN_GPUMIX`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mp-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mq-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mq-power.h

Purpose: `imx8mq-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 13 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX8M (11), IMX8MQ (2).
Representative constants are `IMX8M_POWER_DOMAIN_MIPI`, `IMX8M_POWER_DOMAIN_PCIE1`,
`IMX8M_POWER_DOMAIN_USB_OTG1`, `IMX8M_POWER_DOMAIN_USB_OTG2`, `IMX8M_POWER_DOMAIN_DDR1`,
`IMX8M_POWER_DOMAIN_GPU`, `IMX8M_POWER_DOMAIN_VPU`, `IMX8M_POWER_DOMAIN_DISP`,
`IMX8M_POWER_DOMAIN_GPU`, `IMX8M_POWER_DOMAIN_VPU`, `IMX8M_POWER_DOMAIN_DISP`,
`IMX8M_POWER_DOMAIN_MIPI_CSI1`, `IMX8M_POWER_DOMAIN_MIPI_CSI2`, `IMX8M_POWER_DOMAIN_PCIE2`,
`IMX8MQ_VPUBLK_PD_G1`, `IMX8MQ_VPUBLK_PD_G2`. Function-like helpers are none. Value shape: literal
numeric range 0..10 across 13 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX8MQ_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX8M group`, `IMX8MQ group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 24 lines long. Notable source comments include none. Example value clusters are IMX8M:
`IMX8M_POWER_DOMAIN_MIPI=0`, `IMX8M_POWER_DOMAIN_PCIE1=1`, `IMX8M_POWER_DOMAIN_USB_OTG1=2`,
`IMX8M_POWER_DOMAIN_USB_OTG2=3`; IMX8MQ: `IMX8MQ_VPUBLK_PD_G1=0`, `IMX8MQ_VPUBLK_PD_G2=1`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX8M_POWER_DOMAIN_MIPI`, `IMX8M_POWER_DOMAIN_PCIE1`, `IMX8M_POWER_DOMAIN_USB_OTG1`,
`IMX8M_POWER_DOMAIN_USB_OTG2`, `IMX8M_POWER_DOMAIN_DDR1`, `IMX8M_POWER_DOMAIN_GPU`,
`IMX8M_POWER_DOMAIN_VPU`, `IMX8M_POWER_DOMAIN_DISP`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8mq-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8ulp-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8ulp-power.h

Purpose: `imx8ulp-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 16 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are IMX8ULP (16). Representative
constants are `IMX8ULP_PD_DMA1`, `IMX8ULP_PD_FLEXSPI2`, `IMX8ULP_PD_USB0`, `IMX8ULP_PD_USDHC0`,
`IMX8ULP_PD_USDHC1`, `IMX8ULP_PD_USDHC2_USB1`, `IMX8ULP_PD_DCNANO`, `IMX8ULP_PD_EPDC`,
`IMX8ULP_PD_DMA2`, `IMX8ULP_PD_GPU2D`, `IMX8ULP_PD_GPU3D`, `IMX8ULP_PD_HIFI4`, `IMX8ULP_PD_ISI`,
`IMX8ULP_PD_MIPI_CSI`, `IMX8ULP_PD_MIPI_DSI`, `IMX8ULP_PD_PXP`. Function-like helpers are none.
Value shape: literal numeric range 0..15 across 16 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_IMX8ULP_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX8ULP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 26 lines long. Notable source comments include none. Example value clusters are IMX8ULP:
`IMX8ULP_PD_DMA1=0`, `IMX8ULP_PD_FLEXSPI2=1`, `IMX8ULP_PD_USB0=2`, `IMX8ULP_PD_USDHC0=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`IMX8ULP_PD_DMA1`, `IMX8ULP_PD_FLEXSPI2`, `IMX8ULP_PD_USB0`, `IMX8ULP_PD_USDHC0`,
`IMX8ULP_PD_USDHC1`, `IMX8ULP_PD_USDHC2_USB1`, `IMX8ULP_PD_DCNANO`, `IMX8ULP_PD_EPDC`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/imx8ulp-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/marvell,mmp2.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/marvell,mmp2.h

Purpose: `marvell,mmp2.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 4 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MMP2 (3), MMP3 (1). Representative
constants are `MMP2_POWER_DOMAIN_GPU`, `MMP2_POWER_DOMAIN_AUDIO`, `MMP3_POWER_DOMAIN_CAMERA`,
`MMP2_NR_POWER_DOMAINS`, `MMP2_POWER_DOMAIN_GPU`, `MMP2_POWER_DOMAIN_AUDIO`,
`MMP3_POWER_DOMAIN_CAMERA`, `MMP2_NR_POWER_DOMAINS`. Function-like helpers are none. Value shape:
literal numeric range 0..3 across 4 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DTS_MARVELL_MMP2_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are `MMP2
group`, `MMP3 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 11 lines long. Notable source comments include none. Example value clusters are MMP2:
`MMP2_POWER_DOMAIN_GPU=0`, `MMP2_POWER_DOMAIN_AUDIO=1`, `MMP2_NR_POWER_DOMAINS=3`; MMP3:
`MMP3_POWER_DOMAIN_CAMERA=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MMP2_POWER_DOMAIN_GPU`, `MMP2_POWER_DOMAIN_AUDIO`, `MMP3_POWER_DOMAIN_CAMERA`,
`MMP2_NR_POWER_DOMAINS`. Test signals include dt_binding_check, boot-time genpd attachment, power-
domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/marvell,mmp2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/marvell,pxa1908-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/marvell,pxa1908-power.h

Purpose: `marvell,pxa1908-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PXA1908 (6). Representative
constants are `PXA1908_POWER_DOMAIN_VPU`, `PXA1908_POWER_DOMAIN_GPU`, `PXA1908_POWER_DOMAIN_GPU2D`,
`PXA1908_POWER_DOMAIN_DSI`, `PXA1908_POWER_DOMAIN_ISP`, `PXA1908_POWER_DOMAIN_AUDIO`,
`PXA1908_POWER_DOMAIN_VPU`, `PXA1908_POWER_DOMAIN_GPU`, `PXA1908_POWER_DOMAIN_GPU2D`,
`PXA1908_POWER_DOMAIN_DSI`, `PXA1908_POWER_DOMAIN_ISP`, `PXA1908_POWER_DOMAIN_AUDIO`. Function-like
helpers are none. Value shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DTS_MARVELL_PXA1908_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PXA1908 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 18 lines long. Notable source comments include `Marvell PXA1908 power domains`. Example
value clusters are PXA1908: `PXA1908_POWER_DOMAIN_VPU=0`, `PXA1908_POWER_DOMAIN_GPU=1`,
`PXA1908_POWER_DOMAIN_GPU2D=2`, `PXA1908_POWER_DOMAIN_DSI=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PXA1908_POWER_DOMAIN_VPU`, `PXA1908_POWER_DOMAIN_GPU`, `PXA1908_POWER_DOMAIN_GPU2D`,
`PXA1908_POWER_DOMAIN_DSI`, `PXA1908_POWER_DOMAIN_ISP`, `PXA1908_POWER_DOMAIN_AUDIO`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/marvell,pxa1908-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt6735-power-controller.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt6735-power-controller.h

Purpose: `mediatek,mt6735-power-controller.h` is a Devicetree binding header for a power-domain provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT6735 (7). Representative
constants are `MT6735_POWER_DOMAIN_MD1`, `MT6735_POWER_DOMAIN_CONN`, `MT6735_POWER_DOMAIN_DIS`,
`MT6735_POWER_DOMAIN_MFG`, `MT6735_POWER_DOMAIN_ISP`, `MT6735_POWER_DOMAIN_VDE`,
`MT6735_POWER_DOMAIN_VEN`, `MT6735_POWER_DOMAIN_MD1`, `MT6735_POWER_DOMAIN_CONN`,
`MT6735_POWER_DOMAIN_DIS`, `MT6735_POWER_DOMAIN_MFG`, `MT6735_POWER_DOMAIN_ISP`,
`MT6735_POWER_DOMAIN_VDE`, `MT6735_POWER_DOMAIN_VEN`. Function-like helpers are none. Value shape:
literal numeric range 0..6 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT6735_POWER_CONTROLLER_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `MT6735 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 14 lines long. Notable source comments include none. Example value clusters are MT6735:
`MT6735_POWER_DOMAIN_MD1=0`, `MT6735_POWER_DOMAIN_CONN=1`, `MT6735_POWER_DOMAIN_DIS=2`,
`MT6735_POWER_DOMAIN_MFG=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT6735_POWER_DOMAIN_MD1`, `MT6735_POWER_DOMAIN_CONN`, `MT6735_POWER_DOMAIN_DIS`,
`MT6735_POWER_DOMAIN_MFG`, `MT6735_POWER_DOMAIN_ISP`, `MT6735_POWER_DOMAIN_VDE`,
`MT6735_POWER_DOMAIN_VEN`. Test signals include dt_binding_check, boot-time genpd attachment, power-
domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt6735-power-controller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt6893-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt6893-power.h

Purpose: `mediatek,mt6893-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 24 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT6893 (24). Representative
constants are `MT6893_POWER_DOMAIN_CONN`, `MT6893_POWER_DOMAIN_MFG0`, `MT6893_POWER_DOMAIN_MFG1`,
`MT6893_POWER_DOMAIN_MFG2`, `MT6893_POWER_DOMAIN_MFG3`, `MT6893_POWER_DOMAIN_MFG4`,
`MT6893_POWER_DOMAIN_MFG5`, `MT6893_POWER_DOMAIN_MFG6`, `...`, `MT6893_POWER_DOMAIN_DISP`,
`MT6893_POWER_DOMAIN_AUDIO`, `MT6893_POWER_DOMAIN_ADSP`, `MT6893_POWER_DOMAIN_CAM`,
`MT6893_POWER_DOMAIN_CAM_RAWA`, `MT6893_POWER_DOMAIN_CAM_RAWB`, `MT6893_POWER_DOMAIN_CAM_RAWC`,
`MT6893_POWER_DOMAIN_DP_TX`. Function-like helpers are none. Value shape: literal numeric range
0..23 across 24 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT6893_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT6893 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 35 lines long. Notable source comments include `AngeloGioacchino Del Regno
<angelogioacchino.delregno@collabora.com>`, `_DT_BINDINGS_POWER_MT6893_POWER_H`. Example value
clusters are MT6893: `MT6893_POWER_DOMAIN_CONN=0`, `MT6893_POWER_DOMAIN_MFG0=1`,
`MT6893_POWER_DOMAIN_MFG1=2`, `MT6893_POWER_DOMAIN_MFG2=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT6893_POWER_DOMAIN_CONN`, `MT6893_POWER_DOMAIN_MFG0`, `MT6893_POWER_DOMAIN_MFG1`,
`MT6893_POWER_DOMAIN_MFG2`, `MT6893_POWER_DOMAIN_MFG3`, `MT6893_POWER_DOMAIN_MFG4`,
`MT6893_POWER_DOMAIN_MFG5`, `MT6893_POWER_DOMAIN_MFG6`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt6893-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8188-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8188-power.h

Purpose: `mediatek,mt8188-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 33 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8188 (33). Representative
constants are `MT8188_POWER_DOMAIN_MFG0`, `MT8188_POWER_DOMAIN_MFG1`, `MT8188_POWER_DOMAIN_MFG2`,
`MT8188_POWER_DOMAIN_MFG3`, `MT8188_POWER_DOMAIN_MFG4`, `MT8188_POWER_DOMAIN_PEXTP_MAC_P0`,
`MT8188_POWER_DOMAIN_PEXTP_PHY_TOP`, `MT8188_POWER_DOMAIN_CSIRX_TOP`, `...`,
`MT8188_POWER_DOMAIN_IMG_VCORE`, `MT8188_POWER_DOMAIN_IMG_MAIN`, `MT8188_POWER_DOMAIN_DIP`,
`MT8188_POWER_DOMAIN_IPE`, `MT8188_POWER_DOMAIN_CAM_VCORE`, `MT8188_POWER_DOMAIN_CAM_MAIN`,
`MT8188_POWER_DOMAIN_CAM_SUBA`, `MT8188_POWER_DOMAIN_CAM_SUBB`. Function-like helpers are none.
Value shape: literal numeric range 0..32 across 33 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8188_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT8188 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 44 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT8188_POWER_H`.
Example value clusters are MT8188: `MT8188_POWER_DOMAIN_MFG0=0`, `MT8188_POWER_DOMAIN_MFG1=1`,
`MT8188_POWER_DOMAIN_MFG2=2`, `MT8188_POWER_DOMAIN_MFG3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8188_POWER_DOMAIN_MFG0`, `MT8188_POWER_DOMAIN_MFG1`, `MT8188_POWER_DOMAIN_MFG2`,
`MT8188_POWER_DOMAIN_MFG3`, `MT8188_POWER_DOMAIN_MFG4`, `MT8188_POWER_DOMAIN_PEXTP_MAC_P0`,
`MT8188_POWER_DOMAIN_PEXTP_PHY_TOP`, `MT8188_POWER_DOMAIN_CSIRX_TOP`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8188-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8189-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8189-power.h

Purpose: `mediatek,mt8189-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 26 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8189 (26). Representative
constants are `MT8189_POWER_DOMAIN_CONN`, `MT8189_POWER_DOMAIN_AUDIO`,
`MT8189_POWER_DOMAIN_ADSP_TOP_DORMANT`, `MT8189_POWER_DOMAIN_ADSP_INFRA`,
`MT8189_POWER_DOMAIN_ADSP_AO`, `MT8189_POWER_DOMAIN_MM_INFRA`, `MT8189_POWER_DOMAIN_ISP_IMG1`,
`MT8189_POWER_DOMAIN_ISP_IMG2`, `...`, `MT8189_POWER_DOMAIN_SSUSB`, `MT8189_POWER_DOMAIN_MFG0`,
`MT8189_POWER_DOMAIN_MFG1`, `MT8189_POWER_DOMAIN_MFG2`, `MT8189_POWER_DOMAIN_MFG3`,
`MT8189_POWER_DOMAIN_EDP_TX_DORMANT`, `MT8189_POWER_DOMAIN_PCIE`, `MT8189_POWER_DOMAIN_PCIE_PHY`.
Function-like helpers are none. Value shape: literal numeric range 0..25 across 26 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8189_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`SPM`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 38 lines long. Notable source comments include `SPM`,
`_DT_BINDINGS_POWER_MT8189_POWER_H`. Example value clusters are MT8189:
`MT8189_POWER_DOMAIN_CONN=0`, `MT8189_POWER_DOMAIN_AUDIO=1`,
`MT8189_POWER_DOMAIN_ADSP_TOP_DORMANT=2`, `MT8189_POWER_DOMAIN_ADSP_INFRA=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8189_POWER_DOMAIN_CONN`, `MT8189_POWER_DOMAIN_AUDIO`, `MT8189_POWER_DOMAIN_ADSP_TOP_DORMANT`,
`MT8189_POWER_DOMAIN_ADSP_INFRA`, `MT8189_POWER_DOMAIN_ADSP_AO`, `MT8189_POWER_DOMAIN_MM_INFRA`,
`MT8189_POWER_DOMAIN_ISP_IMG1`, `MT8189_POWER_DOMAIN_ISP_IMG2`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8189-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8196-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8196-power.h

Purpose: `mediatek,mt8196-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 42 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8196 (42). Representative
constants are `MT8196_POWER_DOMAIN_MD`, `MT8196_POWER_DOMAIN_CONN`, `MT8196_POWER_DOMAIN_SSUSB_P0`,
`MT8196_POWER_DOMAIN_SSUSB_DP_PHY_P0`, `MT8196_POWER_DOMAIN_SSUSB_P1`,
`MT8196_POWER_DOMAIN_SSUSB_P23`, `MT8196_POWER_DOMAIN_SSUSB_PHY_P2`,
`MT8196_POWER_DOMAIN_PEXTP_MAC0`, `...`, `MT8196_POWER_DOMAIN_MM_INFRA0`,
`MT8196_POWER_DOMAIN_MM_INFRA1`, `MT8196_POWER_DOMAIN_MM_INFRA_AO`, `MT8196_POWER_DOMAIN_CSI_BS_RX`,
`MT8196_POWER_DOMAIN_CSI_LS_RX`, `MT8196_POWER_DOMAIN_DSI_PHY0`, `MT8196_POWER_DOMAIN_DSI_PHY1`,
`MT8196_POWER_DOMAIN_DSI_PHY2`. Function-like helpers are none. Value shape: literal numeric range
0..22 across 42 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8196_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`SCPSYS Secure Power Manager - Direct Control`, `SCPSYS Secure Power Manager - HW Voter`, `HFRPSYS
MultiMedia Power Control (MMPC) - HW Voter`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 58 lines long. Notable source comments include `AngeloGioacchino Del Regno
<angelogioacchino.delregno@collabora.com>`, `SCPSYS Secure Power Manager - Direct Control`, `SCPSYS
Secure Power Manager - HW Voter`, `HFRPSYS MultiMedia Power Control (MMPC) - HW Voter`,
`_DT_BINDINGS_POWER_MT8196_POWER_H`. Example value clusters are MT8196: `MT8196_POWER_DOMAIN_MD=0`,
`MT8196_POWER_DOMAIN_CONN=1`, `MT8196_POWER_DOMAIN_SSUSB_P0=2`,
`MT8196_POWER_DOMAIN_SSUSB_DP_PHY_P0=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8196_POWER_DOMAIN_MD`, `MT8196_POWER_DOMAIN_CONN`, `MT8196_POWER_DOMAIN_SSUSB_P0`,
`MT8196_POWER_DOMAIN_SSUSB_DP_PHY_P0`, `MT8196_POWER_DOMAIN_SSUSB_P1`,
`MT8196_POWER_DOMAIN_SSUSB_P23`, `MT8196_POWER_DOMAIN_SSUSB_PHY_P2`,
`MT8196_POWER_DOMAIN_PEXTP_MAC0`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8196-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8365-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8365-power.h

Purpose: `mediatek,mt8365-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8365 (9). Representative
constants are `MT8365_POWER_DOMAIN_MM`, `MT8365_POWER_DOMAIN_CONN`, `MT8365_POWER_DOMAIN_MFG`,
`MT8365_POWER_DOMAIN_AUDIO`, `MT8365_POWER_DOMAIN_CAM`, `MT8365_POWER_DOMAIN_DSP`,
`MT8365_POWER_DOMAIN_VDEC`, `MT8365_POWER_DOMAIN_VENC`, `MT8365_POWER_DOMAIN_CONN`,
`MT8365_POWER_DOMAIN_MFG`, `MT8365_POWER_DOMAIN_AUDIO`, `MT8365_POWER_DOMAIN_CAM`,
`MT8365_POWER_DOMAIN_DSP`, `MT8365_POWER_DOMAIN_VDEC`, `MT8365_POWER_DOMAIN_VENC`,
`MT8365_POWER_DOMAIN_APU`. Function-like helpers are none. Value shape: literal numeric range 0..8
across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8365_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT8365 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT8365_POWER_H`.
Example value clusters are MT8365: `MT8365_POWER_DOMAIN_MM=0`, `MT8365_POWER_DOMAIN_CONN=1`,
`MT8365_POWER_DOMAIN_MFG=2`, `MT8365_POWER_DOMAIN_AUDIO=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8365_POWER_DOMAIN_MM`, `MT8365_POWER_DOMAIN_CONN`, `MT8365_POWER_DOMAIN_MFG`,
`MT8365_POWER_DOMAIN_AUDIO`, `MT8365_POWER_DOMAIN_CAM`, `MT8365_POWER_DOMAIN_DSP`,
`MT8365_POWER_DOMAIN_VDEC`, `MT8365_POWER_DOMAIN_VENC`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mediatek,mt8365-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-a1-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-a1-power.h

Purpose: `meson-a1-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 21 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (21). Representative constants
are `PWRC_DSPA_ID`, `PWRC_DSPB_ID`, `PWRC_UART_ID`, `PWRC_DMC_ID`, `PWRC_I2C_ID`, `PWRC_PSRAM_ID`,
`PWRC_ACODEC_ID`, `PWRC_AUDIO_ID`, `...`, `PWRC_IR_ID`, `PWRC_SPICC_ID`, `PWRC_SPIFC_ID`,
`PWRC_USB_ID`, `PWRC_NIC_ID`, `PWRC_PDMIN_ID`, `PWRC_RSA_ID`, `PWRC_MAX_ID`. Function-like helpers
are none. Value shape: literal numeric range 8..28 across 21 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_MESON_A1_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 32 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_DSPA_ID=8`, `PWRC_DSPB_ID=9`, `PWRC_UART_ID=10`, `PWRC_DMC_ID=11`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_DSPA_ID`, `PWRC_DSPB_ID`, `PWRC_UART_ID`, `PWRC_DMC_ID`, `PWRC_I2C_ID`, `PWRC_PSRAM_ID`,
`PWRC_ACODEC_ID`, `PWRC_AUDIO_ID`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-a1-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-axg-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-axg-power.h

Purpose: `meson-axg-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (3). Representative constants
are `PWRC_AXG_VPU_ID`, `PWRC_AXG_ETHERNET_MEM_ID`, `PWRC_AXG_AUDIO_ID`, `PWRC_AXG_VPU_ID`,
`PWRC_AXG_ETHERNET_MEM_ID`, `PWRC_AXG_AUDIO_ID`. Function-like helpers are none. Value shape:
literal numeric range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_MESON_AXG_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 14 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_AXG_VPU_ID=0`, `PWRC_AXG_ETHERNET_MEM_ID=1`, `PWRC_AXG_AUDIO_ID=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_AXG_VPU_ID`, `PWRC_AXG_ETHERNET_MEM_ID`, `PWRC_AXG_AUDIO_ID`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-axg-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-g12a-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-g12a-power.h

Purpose: `meson-g12a-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 4 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (4). Representative constants
are `PWRC_G12A_VPU_ID`, `PWRC_G12A_ETH_ID`, `PWRC_G12A_NNA_ID`, `PWRC_G12A_ISP_ID`,
`PWRC_G12A_VPU_ID`, `PWRC_G12A_ETH_ID`, `PWRC_G12A_NNA_ID`, `PWRC_G12A_ISP_ID`. Function-like
helpers are none. Value shape: literal numeric range 0..3 across 4 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_MESON_G12A_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 15 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_G12A_VPU_ID=0`, `PWRC_G12A_ETH_ID=1`, `PWRC_G12A_NNA_ID=2`, `PWRC_G12A_ISP_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_G12A_VPU_ID`, `PWRC_G12A_ETH_ID`, `PWRC_G12A_NNA_ID`, `PWRC_G12A_ISP_ID`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-g12a-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-gxbb-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-gxbb-power.h

Purpose: `meson-gxbb-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (2). Representative constants
are `PWRC_GXBB_VPU_ID`, `PWRC_GXBB_ETHERNET_MEM_ID`, `PWRC_GXBB_VPU_ID`,
`PWRC_GXBB_ETHERNET_MEM_ID`. Function-like helpers are none. Value shape: literal numeric range 0..1
across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_MESON_GXBB_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 13 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_GXBB_VPU_ID=0`, `PWRC_GXBB_ETHERNET_MEM_ID=1`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_GXBB_VPU_ID`, `PWRC_GXBB_ETHERNET_MEM_ID`. Test signals include dt_binding_check, boot-time
genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-gxbb-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-s4-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-s4-power.h

Purpose: `meson-s4-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (8). Representative constants
are `PWRC_S4_DOS_HEVC_ID`, `PWRC_S4_DOS_VDEC_ID`, `PWRC_S4_VPU_HDMI_ID`, `PWRC_S4_USB_COMB_ID`,
`PWRC_S4_GE2D_ID`, `PWRC_S4_ETH_ID`, `PWRC_S4_DEMOD_ID`, `PWRC_S4_AUDIO_ID`, `PWRC_S4_DOS_HEVC_ID`,
`PWRC_S4_DOS_VDEC_ID`, `PWRC_S4_VPU_HDMI_ID`, `PWRC_S4_USB_COMB_ID`, `PWRC_S4_GE2D_ID`,
`PWRC_S4_ETH_ID`, `PWRC_S4_DEMOD_ID`, `PWRC_S4_AUDIO_ID`. Function-like helpers are none. Value
shape: literal numeric range 0..7 across 8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_MESON_S4_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_S4_DOS_HEVC_ID=0`, `PWRC_S4_DOS_VDEC_ID=1`, `PWRC_S4_VPU_HDMI_ID=2`, `PWRC_S4_USB_COMB_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_S4_DOS_HEVC_ID`, `PWRC_S4_DOS_VDEC_ID`, `PWRC_S4_VPU_HDMI_ID`, `PWRC_S4_USB_COMB_ID`,
`PWRC_S4_GE2D_ID`, `PWRC_S4_ETH_ID`, `PWRC_S4_DEMOD_ID`, `PWRC_S4_AUDIO_ID`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-s4-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-sm1-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-sm1-power.h

Purpose: `meson-sm1-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (7). Representative constants
are `PWRC_SM1_VPU_ID`, `PWRC_SM1_NNA_ID`, `PWRC_SM1_USB_ID`, `PWRC_SM1_PCIE_ID`, `PWRC_SM1_GE2D_ID`,
`PWRC_SM1_AUDIO_ID`, `PWRC_SM1_ETH_ID`, `PWRC_SM1_VPU_ID`, `PWRC_SM1_NNA_ID`, `PWRC_SM1_USB_ID`,
`PWRC_SM1_PCIE_ID`, `PWRC_SM1_GE2D_ID`, `PWRC_SM1_AUDIO_ID`, `PWRC_SM1_ETH_ID`. Function-like
helpers are none. Value shape: literal numeric range 0..6 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_MESON_SM1_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 18 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_SM1_VPU_ID=0`, `PWRC_SM1_NNA_ID=1`, `PWRC_SM1_USB_ID=2`, `PWRC_SM1_PCIE_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_SM1_VPU_ID`, `PWRC_SM1_NNA_ID`, `PWRC_SM1_USB_ID`, `PWRC_SM1_PCIE_ID`, `PWRC_SM1_GE2D_ID`,
`PWRC_SM1_AUDIO_ID`, `PWRC_SM1_ETH_ID`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-sm1-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson8-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/meson8-power.h

Purpose: `meson8-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (3). Representative constants
are `PWRC_MESON8_VPU_ID`, `PWRC_MESON8_ETHERNET_MEM_ID`, `PWRC_MESON8_AUDIO_DSP_MEM_ID`,
`PWRC_MESON8_VPU_ID`, `PWRC_MESON8_ETHERNET_MEM_ID`, `PWRC_MESON8_AUDIO_DSP_MEM_ID`. Function-like
helpers are none. Value shape: literal numeric range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_MESON8_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are `PWRC
group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 13 lines long. Notable source comments include `_DT_BINDINGS_MESON8_POWER_H`. Example
value clusters are PWRC: `PWRC_MESON8_VPU_ID=0`, `PWRC_MESON8_ETHERNET_MEM_ID=1`,
`PWRC_MESON8_AUDIO_DSP_MEM_ID=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_MESON8_VPU_ID`, `PWRC_MESON8_ETHERNET_MEM_ID`, `PWRC_MESON8_AUDIO_DSP_MEM_ID`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/meson8-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt2701-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt2701-power.h

Purpose: `mt2701-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT2701 (9). Representative
constants are `MT2701_POWER_DOMAIN_CONN`, `MT2701_POWER_DOMAIN_DISP`, `MT2701_POWER_DOMAIN_MFG`,
`MT2701_POWER_DOMAIN_VDEC`, `MT2701_POWER_DOMAIN_ISP`, `MT2701_POWER_DOMAIN_BDP`,
`MT2701_POWER_DOMAIN_ETH`, `MT2701_POWER_DOMAIN_HIF`, `MT2701_POWER_DOMAIN_DISP`,
`MT2701_POWER_DOMAIN_MFG`, `MT2701_POWER_DOMAIN_VDEC`, `MT2701_POWER_DOMAIN_ISP`,
`MT2701_POWER_DOMAIN_BDP`, `MT2701_POWER_DOMAIN_ETH`, `MT2701_POWER_DOMAIN_HIF`,
`MT2701_POWER_DOMAIN_IFR_MSC`. Function-like helpers are none. Value shape: literal numeric range
0..8 across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT2701_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT2701 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT2701_POWER_H`.
Example value clusters are MT2701: `MT2701_POWER_DOMAIN_CONN=0`, `MT2701_POWER_DOMAIN_DISP=1`,
`MT2701_POWER_DOMAIN_MFG=2`, `MT2701_POWER_DOMAIN_VDEC=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT2701_POWER_DOMAIN_CONN`, `MT2701_POWER_DOMAIN_DISP`, `MT2701_POWER_DOMAIN_MFG`,
`MT2701_POWER_DOMAIN_VDEC`, `MT2701_POWER_DOMAIN_ISP`, `MT2701_POWER_DOMAIN_BDP`,
`MT2701_POWER_DOMAIN_ETH`, `MT2701_POWER_DOMAIN_HIF`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt2701-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt2712-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt2712-power.h

Purpose: `mt2712-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT2712 (11). Representative
constants are `MT2712_POWER_DOMAIN_MM`, `MT2712_POWER_DOMAIN_VDEC`, `MT2712_POWER_DOMAIN_VENC`,
`MT2712_POWER_DOMAIN_ISP`, `MT2712_POWER_DOMAIN_AUDIO`, `MT2712_POWER_DOMAIN_USB`,
`MT2712_POWER_DOMAIN_USB2`, `MT2712_POWER_DOMAIN_MFG`, `MT2712_POWER_DOMAIN_ISP`,
`MT2712_POWER_DOMAIN_AUDIO`, `MT2712_POWER_DOMAIN_USB`, `MT2712_POWER_DOMAIN_USB2`,
`MT2712_POWER_DOMAIN_MFG`, `MT2712_POWER_DOMAIN_MFG_SC1`, `MT2712_POWER_DOMAIN_MFG_SC2`,
`MT2712_POWER_DOMAIN_MFG_SC3`. Function-like helpers are none. Value shape: literal numeric range
0..10 across 11 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT2712_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT2712 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 21 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT2712_POWER_H`.
Example value clusters are MT2712: `MT2712_POWER_DOMAIN_MM=0`, `MT2712_POWER_DOMAIN_VDEC=1`,
`MT2712_POWER_DOMAIN_VENC=2`, `MT2712_POWER_DOMAIN_ISP=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT2712_POWER_DOMAIN_MM`, `MT2712_POWER_DOMAIN_VDEC`, `MT2712_POWER_DOMAIN_VENC`,
`MT2712_POWER_DOMAIN_ISP`, `MT2712_POWER_DOMAIN_AUDIO`, `MT2712_POWER_DOMAIN_USB`,
`MT2712_POWER_DOMAIN_USB2`, `MT2712_POWER_DOMAIN_MFG`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt2712-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt6765-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt6765-power.h

Purpose: `mt6765-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT6765 (8). Representative
constants are `MT6765_POWER_DOMAIN_CONN`, `MT6765_POWER_DOMAIN_MM`, `MT6765_POWER_DOMAIN_MFG_ASYNC`,
`MT6765_POWER_DOMAIN_ISP`, `MT6765_POWER_DOMAIN_MFG`, `MT6765_POWER_DOMAIN_MFG_CORE0`,
`MT6765_POWER_DOMAIN_CAM`, `MT6765_POWER_DOMAIN_VCODEC`, `MT6765_POWER_DOMAIN_CONN`,
`MT6765_POWER_DOMAIN_MM`, `MT6765_POWER_DOMAIN_MFG_ASYNC`, `MT6765_POWER_DOMAIN_ISP`,
`MT6765_POWER_DOMAIN_MFG`, `MT6765_POWER_DOMAIN_MFG_CORE0`, `MT6765_POWER_DOMAIN_CAM`,
`MT6765_POWER_DOMAIN_VCODEC`. Function-like helpers are none. Value shape: literal numeric range
0..7 across 8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT6765_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT6765 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 14 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT6765_POWER_H`.
Example value clusters are MT6765: `MT6765_POWER_DOMAIN_CONN=0`, `MT6765_POWER_DOMAIN_MM=1`,
`MT6765_POWER_DOMAIN_MFG_ASYNC=2`, `MT6765_POWER_DOMAIN_ISP=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT6765_POWER_DOMAIN_CONN`, `MT6765_POWER_DOMAIN_MM`, `MT6765_POWER_DOMAIN_MFG_ASYNC`,
`MT6765_POWER_DOMAIN_ISP`, `MT6765_POWER_DOMAIN_MFG`, `MT6765_POWER_DOMAIN_MFG_CORE0`,
`MT6765_POWER_DOMAIN_CAM`, `MT6765_POWER_DOMAIN_VCODEC`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt6765-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt6795-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt6795-power.h

Purpose: `mt6795-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 10 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT6795 (10). Representative
constants are `MT6795_POWER_DOMAIN_MM`, `MT6795_POWER_DOMAIN_VDEC`, `MT6795_POWER_DOMAIN_VENC`,
`MT6795_POWER_DOMAIN_ISP`, `MT6795_POWER_DOMAIN_MJC`, `MT6795_POWER_DOMAIN_AUDIO`,
`MT6795_POWER_DOMAIN_MFG_ASYNC`, `MT6795_POWER_DOMAIN_MFG_2D`, `MT6795_POWER_DOMAIN_VENC`,
`MT6795_POWER_DOMAIN_ISP`, `MT6795_POWER_DOMAIN_MJC`, `MT6795_POWER_DOMAIN_AUDIO`,
`MT6795_POWER_DOMAIN_MFG_ASYNC`, `MT6795_POWER_DOMAIN_MFG_2D`, `MT6795_POWER_DOMAIN_MFG`,
`MT6795_POWER_DOMAIN_MODEM`. Function-like helpers are none. Value shape: literal numeric range 0..9
across 10 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT6795_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT6795 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 16 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT6795_POWER_H`.
Example value clusters are MT6795: `MT6795_POWER_DOMAIN_MM=0`, `MT6795_POWER_DOMAIN_VDEC=1`,
`MT6795_POWER_DOMAIN_VENC=2`, `MT6795_POWER_DOMAIN_ISP=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT6795_POWER_DOMAIN_MM`, `MT6795_POWER_DOMAIN_VDEC`, `MT6795_POWER_DOMAIN_VENC`,
`MT6795_POWER_DOMAIN_ISP`, `MT6795_POWER_DOMAIN_MJC`, `MT6795_POWER_DOMAIN_AUDIO`,
`MT6795_POWER_DOMAIN_MFG_ASYNC`, `MT6795_POWER_DOMAIN_MFG_2D`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt6795-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt6797-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt6797-power.h

Purpose: `mt6797-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 12 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT6797 (12). Representative
constants are `MT6797_POWER_DOMAIN_VDEC`, `MT6797_POWER_DOMAIN_VENC`, `MT6797_POWER_DOMAIN_ISP`,
`MT6797_POWER_DOMAIN_MM`, `MT6797_POWER_DOMAIN_AUDIO`, `MT6797_POWER_DOMAIN_MFG_ASYNC`,
`MT6797_POWER_DOMAIN_MFG`, `MT6797_POWER_DOMAIN_MFG_CORE0`, `MT6797_POWER_DOMAIN_AUDIO`,
`MT6797_POWER_DOMAIN_MFG_ASYNC`, `MT6797_POWER_DOMAIN_MFG`, `MT6797_POWER_DOMAIN_MFG_CORE0`,
`MT6797_POWER_DOMAIN_MFG_CORE1`, `MT6797_POWER_DOMAIN_MFG_CORE2`, `MT6797_POWER_DOMAIN_MFG_CORE3`,
`MT6797_POWER_DOMAIN_MJC`. Function-like helpers are none. Value shape: literal numeric range 0..11
across 12 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT6797_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT6797 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 23 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT6797_POWER_H`.
Example value clusters are MT6797: `MT6797_POWER_DOMAIN_VDEC=0`, `MT6797_POWER_DOMAIN_VENC=1`,
`MT6797_POWER_DOMAIN_ISP=2`, `MT6797_POWER_DOMAIN_MM=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT6797_POWER_DOMAIN_VDEC`, `MT6797_POWER_DOMAIN_VENC`, `MT6797_POWER_DOMAIN_ISP`,
`MT6797_POWER_DOMAIN_MM`, `MT6797_POWER_DOMAIN_AUDIO`, `MT6797_POWER_DOMAIN_MFG_ASYNC`,
`MT6797_POWER_DOMAIN_MFG`, `MT6797_POWER_DOMAIN_MFG_CORE0`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt6797-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt7622-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt7622-power.h

Purpose: `mt7622-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT7622 (5). Representative
constants are `MT7622_POWER_DOMAIN_ETHSYS`, `MT7622_POWER_DOMAIN_HIF0`, `MT7622_POWER_DOMAIN_HIF1`,
`MT7622_POWER_DOMAIN_WB`, `MT7622_POWER_DOMAIN_AUDIO`, `MT7622_POWER_DOMAIN_ETHSYS`,
`MT7622_POWER_DOMAIN_HIF0`, `MT7622_POWER_DOMAIN_HIF1`, `MT7622_POWER_DOMAIN_WB`,
`MT7622_POWER_DOMAIN_AUDIO`. Function-like helpers are none. Value shape: literal numeric range 0..4
across 5 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT7622_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT7622 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 15 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT7622_POWER_H`.
Example value clusters are MT7622: `MT7622_POWER_DOMAIN_ETHSYS=0`, `MT7622_POWER_DOMAIN_HIF0=1`,
`MT7622_POWER_DOMAIN_HIF1=2`, `MT7622_POWER_DOMAIN_WB=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT7622_POWER_DOMAIN_ETHSYS`, `MT7622_POWER_DOMAIN_HIF0`, `MT7622_POWER_DOMAIN_HIF1`,
`MT7622_POWER_DOMAIN_WB`, `MT7622_POWER_DOMAIN_AUDIO`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt7622-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt7623a-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt7623a-power.h

Purpose: `mt7623a-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 4 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT7623A (4). Representative
constants are `MT7623A_POWER_DOMAIN_CONN`, `MT7623A_POWER_DOMAIN_ETH`, `MT7623A_POWER_DOMAIN_HIF`,
`MT7623A_POWER_DOMAIN_IFR_MSC`, `MT7623A_POWER_DOMAIN_CONN`, `MT7623A_POWER_DOMAIN_ETH`,
`MT7623A_POWER_DOMAIN_HIF`, `MT7623A_POWER_DOMAIN_IFR_MSC`. Function-like helpers are none. Value
shape: literal numeric range 0..3 across 4 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT7623A_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MT7623A group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 10 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT7623A_POWER_H`.
Example value clusters are MT7623A: `MT7623A_POWER_DOMAIN_CONN=0`, `MT7623A_POWER_DOMAIN_ETH=1`,
`MT7623A_POWER_DOMAIN_HIF=2`, `MT7623A_POWER_DOMAIN_IFR_MSC=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT7623A_POWER_DOMAIN_CONN`, `MT7623A_POWER_DOMAIN_ETH`, `MT7623A_POWER_DOMAIN_HIF`,
`MT7623A_POWER_DOMAIN_IFR_MSC`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt7623a-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8167-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8167-power.h

Purpose: `mt8167-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8167 (7). Representative
constants are `MT8167_POWER_DOMAIN_MM`, `MT8167_POWER_DOMAIN_VDEC`, `MT8167_POWER_DOMAIN_ISP`,
`MT8167_POWER_DOMAIN_CONN`, `MT8167_POWER_DOMAIN_MFG_ASYNC`, `MT8167_POWER_DOMAIN_MFG_2D`,
`MT8167_POWER_DOMAIN_MFG`, `MT8167_POWER_DOMAIN_MM`, `MT8167_POWER_DOMAIN_VDEC`,
`MT8167_POWER_DOMAIN_ISP`, `MT8167_POWER_DOMAIN_CONN`, `MT8167_POWER_DOMAIN_MFG_ASYNC`,
`MT8167_POWER_DOMAIN_MFG_2D`, `MT8167_POWER_DOMAIN_MFG`. Function-like helpers are none. Value
shape: literal numeric range 0..6 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8167_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT8167 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 17 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT8167_POWER_H`.
Example value clusters are MT8167: `MT8167_POWER_DOMAIN_MM=0`, `MT8167_POWER_DOMAIN_VDEC=1`,
`MT8167_POWER_DOMAIN_ISP=2`, `MT8167_POWER_DOMAIN_CONN=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8167_POWER_DOMAIN_MM`, `MT8167_POWER_DOMAIN_VDEC`, `MT8167_POWER_DOMAIN_ISP`,
`MT8167_POWER_DOMAIN_CONN`, `MT8167_POWER_DOMAIN_MFG_ASYNC`, `MT8167_POWER_DOMAIN_MFG_2D`,
`MT8167_POWER_DOMAIN_MFG`. Test signals include dt_binding_check, boot-time genpd attachment, power-
domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8167-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8173-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8173-power.h

Purpose: `mt8173-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 10 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8173 (10). Representative
constants are `MT8173_POWER_DOMAIN_VDEC`, `MT8173_POWER_DOMAIN_VENC`, `MT8173_POWER_DOMAIN_ISP`,
`MT8173_POWER_DOMAIN_MM`, `MT8173_POWER_DOMAIN_VENC_LT`, `MT8173_POWER_DOMAIN_AUDIO`,
`MT8173_POWER_DOMAIN_USB`, `MT8173_POWER_DOMAIN_MFG_ASYNC`, `MT8173_POWER_DOMAIN_ISP`,
`MT8173_POWER_DOMAIN_MM`, `MT8173_POWER_DOMAIN_VENC_LT`, `MT8173_POWER_DOMAIN_AUDIO`,
`MT8173_POWER_DOMAIN_USB`, `MT8173_POWER_DOMAIN_MFG_ASYNC`, `MT8173_POWER_DOMAIN_MFG_2D`,
`MT8173_POWER_DOMAIN_MFG`. Function-like helpers are none. Value shape: literal numeric range 0..9
across 10 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8173_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT8173 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 16 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT8173_POWER_H`.
Example value clusters are MT8173: `MT8173_POWER_DOMAIN_VDEC=0`, `MT8173_POWER_DOMAIN_VENC=1`,
`MT8173_POWER_DOMAIN_ISP=2`, `MT8173_POWER_DOMAIN_MM=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8173_POWER_DOMAIN_VDEC`, `MT8173_POWER_DOMAIN_VENC`, `MT8173_POWER_DOMAIN_ISP`,
`MT8173_POWER_DOMAIN_MM`, `MT8173_POWER_DOMAIN_VENC_LT`, `MT8173_POWER_DOMAIN_AUDIO`,
`MT8173_POWER_DOMAIN_USB`, `MT8173_POWER_DOMAIN_MFG_ASYNC`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8173-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8183-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8183-power.h

Purpose: `mt8183-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 15 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8183 (15). Representative
constants are `MT8183_POWER_DOMAIN_AUDIO`, `MT8183_POWER_DOMAIN_CONN`,
`MT8183_POWER_DOMAIN_MFG_ASYNC`, `MT8183_POWER_DOMAIN_MFG`, `MT8183_POWER_DOMAIN_MFG_CORE0`,
`MT8183_POWER_DOMAIN_MFG_CORE1`, `MT8183_POWER_DOMAIN_MFG_2D`, `MT8183_POWER_DOMAIN_DISP`,
`MT8183_POWER_DOMAIN_DISP`, `MT8183_POWER_DOMAIN_CAM`, `MT8183_POWER_DOMAIN_ISP`,
`MT8183_POWER_DOMAIN_VDEC`, `MT8183_POWER_DOMAIN_VENC`, `MT8183_POWER_DOMAIN_VPU_TOP`,
`MT8183_POWER_DOMAIN_VPU_CORE0`, `MT8183_POWER_DOMAIN_VPU_CORE1`. Function-like helpers are none.
Value shape: literal numeric range 0..14 across 15 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8183_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT8183 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 26 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT8183_POWER_H`.
Example value clusters are MT8183: `MT8183_POWER_DOMAIN_AUDIO=0`, `MT8183_POWER_DOMAIN_CONN=1`,
`MT8183_POWER_DOMAIN_MFG_ASYNC=2`, `MT8183_POWER_DOMAIN_MFG=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8183_POWER_DOMAIN_AUDIO`, `MT8183_POWER_DOMAIN_CONN`, `MT8183_POWER_DOMAIN_MFG_ASYNC`,
`MT8183_POWER_DOMAIN_MFG`, `MT8183_POWER_DOMAIN_MFG_CORE0`, `MT8183_POWER_DOMAIN_MFG_CORE1`,
`MT8183_POWER_DOMAIN_MFG_2D`, `MT8183_POWER_DOMAIN_DISP`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8183-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8186-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8186-power.h

Purpose: `mt8186-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 21 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8186 (21). Representative
constants are `MT8186_POWER_DOMAIN_MFG0`, `MT8186_POWER_DOMAIN_MFG1`, `MT8186_POWER_DOMAIN_MFG2`,
`MT8186_POWER_DOMAIN_MFG3`, `MT8186_POWER_DOMAIN_SSUSB`, `MT8186_POWER_DOMAIN_SSUSB_P1`,
`MT8186_POWER_DOMAIN_DIS`, `MT8186_POWER_DOMAIN_IMG`, `...`, `MT8186_POWER_DOMAIN_VENC`,
`MT8186_POWER_DOMAIN_VDEC`, `MT8186_POWER_DOMAIN_WPE`, `MT8186_POWER_DOMAIN_CONN_ON`,
`MT8186_POWER_DOMAIN_CSIRX_TOP`, `MT8186_POWER_DOMAIN_ADSP_AO`, `MT8186_POWER_DOMAIN_ADSP_INFRA`,
`MT8186_POWER_DOMAIN_ADSP_TOP`. Function-like helpers are none. Value shape: literal numeric range
0..20 across 21 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8186_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT8186 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 32 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT8186_POWER_H`.
Example value clusters are MT8186: `MT8186_POWER_DOMAIN_MFG0=0`, `MT8186_POWER_DOMAIN_MFG1=1`,
`MT8186_POWER_DOMAIN_MFG2=2`, `MT8186_POWER_DOMAIN_MFG3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8186_POWER_DOMAIN_MFG0`, `MT8186_POWER_DOMAIN_MFG1`, `MT8186_POWER_DOMAIN_MFG2`,
`MT8186_POWER_DOMAIN_MFG3`, `MT8186_POWER_DOMAIN_SSUSB`, `MT8186_POWER_DOMAIN_SSUSB_P1`,
`MT8186_POWER_DOMAIN_DIS`, `MT8186_POWER_DOMAIN_IMG`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8186-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8192-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8192-power.h

Purpose: `mt8192-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 21 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8192 (21). Representative
constants are `MT8192_POWER_DOMAIN_AUDIO`, `MT8192_POWER_DOMAIN_CONN`, `MT8192_POWER_DOMAIN_MFG0`,
`MT8192_POWER_DOMAIN_MFG1`, `MT8192_POWER_DOMAIN_MFG2`, `MT8192_POWER_DOMAIN_MFG3`,
`MT8192_POWER_DOMAIN_MFG4`, `MT8192_POWER_DOMAIN_MFG5`, `...`, `MT8192_POWER_DOMAIN_MDP`,
`MT8192_POWER_DOMAIN_VENC`, `MT8192_POWER_DOMAIN_VDEC`, `MT8192_POWER_DOMAIN_VDEC2`,
`MT8192_POWER_DOMAIN_CAM`, `MT8192_POWER_DOMAIN_CAM_RAWA`, `MT8192_POWER_DOMAIN_CAM_RAWB`,
`MT8192_POWER_DOMAIN_CAM_RAWC`. Function-like helpers are none. Value shape: literal numeric range
0..20 across 21 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8192_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT8192 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 32 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT8192_POWER_H`.
Example value clusters are MT8192: `MT8192_POWER_DOMAIN_AUDIO=0`, `MT8192_POWER_DOMAIN_CONN=1`,
`MT8192_POWER_DOMAIN_MFG0=2`, `MT8192_POWER_DOMAIN_MFG1=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8192_POWER_DOMAIN_AUDIO`, `MT8192_POWER_DOMAIN_CONN`, `MT8192_POWER_DOMAIN_MFG0`,
`MT8192_POWER_DOMAIN_MFG1`, `MT8192_POWER_DOMAIN_MFG2`, `MT8192_POWER_DOMAIN_MFG3`,
`MT8192_POWER_DOMAIN_MFG4`, `MT8192_POWER_DOMAIN_MFG5`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8192-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8195-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8195-power.h

Purpose: `mt8195-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 35 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are MT8195 (35). Representative
constants are `MT8195_POWER_DOMAIN_PCIE_MAC_P0`, `MT8195_POWER_DOMAIN_PCIE_MAC_P1`,
`MT8195_POWER_DOMAIN_PCIE_PHY`, `MT8195_POWER_DOMAIN_SSUSB_PCIE_PHY`,
`MT8195_POWER_DOMAIN_CSI_RX_TOP`, `MT8195_POWER_DOMAIN_ETHER`, `MT8195_POWER_DOMAIN_ADSP`,
`MT8195_POWER_DOMAIN_AUDIO`, `...`, `MT8195_POWER_DOMAIN_VENC_CORE1`, `MT8195_POWER_DOMAIN_IMG`,
`MT8195_POWER_DOMAIN_DIP`, `MT8195_POWER_DOMAIN_IPE`, `MT8195_POWER_DOMAIN_CAM`,
`MT8195_POWER_DOMAIN_CAM_RAWA`, `MT8195_POWER_DOMAIN_CAM_RAWB`, `MT8195_POWER_DOMAIN_CAM_MRAW`.
Function-like helpers are none. Value shape: literal numeric range 0..34 across 35 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_MT8195_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT8195 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 46 lines long. Notable source comments include `_DT_BINDINGS_POWER_MT8195_POWER_H`.
Example value clusters are MT8195: `MT8195_POWER_DOMAIN_PCIE_MAC_P0=0`,
`MT8195_POWER_DOMAIN_PCIE_MAC_P1=1`, `MT8195_POWER_DOMAIN_PCIE_PHY=2`,
`MT8195_POWER_DOMAIN_SSUSB_PCIE_PHY=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`MT8195_POWER_DOMAIN_PCIE_MAC_P0`, `MT8195_POWER_DOMAIN_PCIE_MAC_P1`,
`MT8195_POWER_DOMAIN_PCIE_PHY`, `MT8195_POWER_DOMAIN_SSUSB_PCIE_PHY`,
`MT8195_POWER_DOMAIN_CSI_RX_TOP`, `MT8195_POWER_DOMAIN_ETHER`, `MT8195_POWER_DOMAIN_ADSP`,
`MT8195_POWER_DOMAIN_AUDIO`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/mt8195-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/nvidia,tegra264-bpmp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/nvidia,tegra264-bpmp.h

Purpose: `nvidia,tegra264-bpmp.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 15 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are TEGRA264 (15). Representative
constants are `TEGRA264_POWER_DOMAIN_DISP`, `TEGRA264_POWER_DOMAIN_AUD`,
`TEGRA264_POWER_DOMAIN_XUSB_SS`, `TEGRA264_POWER_DOMAIN_XUSB_DEV`,
`TEGRA264_POWER_DOMAIN_XUSB_HOST`, `TEGRA264_POWER_DOMAIN_MGBE0`, `TEGRA264_POWER_DOMAIN_MGBE1`,
`TEGRA264_POWER_DOMAIN_MGBE2`, `TEGRA264_POWER_DOMAIN_MGBE2`, `TEGRA264_POWER_DOMAIN_MGBE3`,
`TEGRA264_POWER_DOMAIN_VI`, `TEGRA264_POWER_DOMAIN_VIC`, `TEGRA264_POWER_DOMAIN_ISP0`,
`TEGRA264_POWER_DOMAIN_ISP1`, `TEGRA264_POWER_DOMAIN_PVA0`, `TEGRA264_POWER_DOMAIN_GPU`. Function-
like helpers are none. Value shape: literal numeric range 1..22 across 15 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_POWER_NVIDIA_TEGRA264_BPMP_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `reserved 3:9`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 24 lines long. Notable source comments include `reserved 3:9`,
`DT_BINDINGS_POWER_NVIDIA_TEGRA264_BPMP_H`. Example value clusters are TEGRA264:
`TEGRA264_POWER_DOMAIN_DISP=1`, `TEGRA264_POWER_DOMAIN_AUD=2`, `TEGRA264_POWER_DOMAIN_XUSB_SS=10`,
`TEGRA264_POWER_DOMAIN_XUSB_DEV=11`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`TEGRA264_POWER_DOMAIN_DISP`, `TEGRA264_POWER_DOMAIN_AUD`, `TEGRA264_POWER_DOMAIN_XUSB_SS`,
`TEGRA264_POWER_DOMAIN_XUSB_DEV`, `TEGRA264_POWER_DOMAIN_XUSB_HOST`, `TEGRA264_POWER_DOMAIN_MGBE0`,
`TEGRA264_POWER_DOMAIN_MGBE1`, `TEGRA264_POWER_DOMAIN_MGBE2`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/nvidia,tegra264-bpmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s500-powergate.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s500-powergate.h

Purpose: `owl-s500-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are S500 (9). Representative constants
are `S500_PD_VDE`, `S500_PD_VCE_SI`, `S500_PD_USB2_1`, `S500_PD_CPU2`, `S500_PD_CPU3`,
`S500_PD_DMA`, `S500_PD_DS`, `S500_PD_USB3`, `S500_PD_VCE_SI`, `S500_PD_USB2_1`, `S500_PD_CPU2`,
`S500_PD_CPU3`, `S500_PD_DMA`, `S500_PD_DS`, `S500_PD_USB3`, `S500_PD_USB2_0`. Function-like helpers
are none. Value shape: literal numeric range 0..8 across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_POWER_OWL_S500_POWERGATE_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `S500 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include none. Example value clusters are S500:
`S500_PD_VDE=0`, `S500_PD_VCE_SI=1`, `S500_PD_USB2_1=2`, `S500_PD_CPU2=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`S500_PD_VDE`, `S500_PD_VCE_SI`, `S500_PD_USB2_1`, `S500_PD_CPU2`, `S500_PD_CPU3`, `S500_PD_DMA`,
`S500_PD_DS`, `S500_PD_USB3`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s500-powergate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s700-powergate.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s700-powergate.h

Purpose: `owl-s700-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are S700 (8). Representative constants
are `S700_PD_VDE`, `S700_PD_VCE_SI`, `S700_PD_USB2_1`, `S700_PD_HDE`, `S700_PD_DMA`, `S700_PD_DS`,
`S700_PD_USB3`, `S700_PD_USB2_0`, `S700_PD_VDE`, `S700_PD_VCE_SI`, `S700_PD_USB2_1`, `S700_PD_HDE`,
`S700_PD_DMA`, `S700_PD_DS`, `S700_PD_USB3`, `S700_PD_USB2_0`. Function-like helpers are none. Value
shape: literal numeric range 0..7 across 8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_POWER_OWL_S700_POWERGATE_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `S700 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include `Actions Semi S700 SPS`. Example value
clusters are S700: `S700_PD_VDE=0`, `S700_PD_VCE_SI=1`, `S700_PD_USB2_1=2`, `S700_PD_HDE=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`S700_PD_VDE`, `S700_PD_VCE_SI`, `S700_PD_USB2_1`, `S700_PD_HDE`, `S700_PD_DMA`, `S700_PD_DS`,
`S700_PD_USB3`, `S700_PD_USB2_0`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s700-powergate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s900-powergate.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s900-powergate.h

Purpose: `owl-s900-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 12 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are S900 (12). Representative constants
are `S900_PD_GPU_B`, `S900_PD_VCE`, `S900_PD_SENSOR`, `S900_PD_VDE`, `S900_PD_HDE`, `S900_PD_USB3`,
`S900_PD_DDR0`, `S900_PD_DDR1`, `S900_PD_HDE`, `S900_PD_USB3`, `S900_PD_DDR0`, `S900_PD_DDR1`,
`S900_PD_DE`, `S900_PD_NAND`, `S900_PD_USB2_H0`, `S900_PD_USB2_H1`. Function-like helpers are none.
Value shape: literal numeric range 0..11 across 12 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_POWER_OWL_S900_POWERGATE_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `S900 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 23 lines long. Notable source comments include `Actions Semi S900 SPS`. Example value
clusters are S900: `S900_PD_GPU_B=0`, `S900_PD_VCE=1`, `S900_PD_SENSOR=2`, `S900_PD_VDE=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`S900_PD_GPU_B`, `S900_PD_VCE`, `S900_PD_SENSOR`, `S900_PD_VDE`, `S900_PD_HDE`, `S900_PD_USB3`,
`S900_PD_DDR0`, `S900_PD_DDR1`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/owl-s900-powergate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/px30-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/px30-power.h

Purpose: `px30-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 16 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PX30 (16). Representative constants
are `PX30_PD_A35_0`, `PX30_PD_A35_1`, `PX30_PD_A35_2`, `PX30_PD_A35_3`, `PX30_PD_SCU`,
`PX30_PD_USB`, `PX30_PD_DDR`, `PX30_PD_SDCARD`, `PX30_PD_CRYPTO`, `PX30_PD_GMAC`,
`PX30_PD_MMC_NAND`, `PX30_PD_VPU`, `PX30_PD_VO`, `PX30_PD_VI`, `PX30_PD_GPU`, `PX30_PD_PMU`.
Function-like helpers are none. Value shape: literal numeric range 0..15 across 16 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_PX30_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_LOGIC`, `VD_PMU`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 27 lines long. Notable source comments include `VD_CORE`, `VD_LOGIC`, `VD_PMU`. Example
value clusters are PX30: `PX30_PD_A35_0=0`, `PX30_PD_A35_1=1`, `PX30_PD_A35_2=2`, `PX30_PD_A35_3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PX30_PD_A35_0`, `PX30_PD_A35_1`, `PX30_PD_A35_2`, `PX30_PD_A35_3`, `PX30_PD_SCU`, `PX30_PD_USB`,
`PX30_PD_DDR`, `PX30_PD_SDCARD`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/px30-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/qcom,rpmhpd.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/qcom,rpmhpd.h

Purpose: `qcom,rpmhpd.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 229 `#define`s covering power-domain IDs, power-
gate IDs, or performance-state constants. The main macro families are RPMH (40), RPMHPD (23),
SA8775P (17), SC8280XP (17), SM8550 (14), SM8350 (13), SM8450 (13), SM8150 (11), SC8180X (11),
SM8250 (10). Representative constants are `RPMHPD_CX`, `RPMHPD_CX_AO`, `RPMHPD_EBI`, `RPMHPD_GFX`,
`RPMHPD_LCX`, `RPMHPD_LMX`, `RPMHPD_MMCX`, `RPMHPD_MMCX_AO`, `...`, `SC8280XP_MSS`, `SC8280XP_MX`,
`SC8280XP_MXC`, `SC8280XP_MX_AO`, `SC8280XP_NSP`, `SC8280XP_QPHY`, `SC8280XP_XO`, `SC8280XP_MXC_AO`.
Function-like helpers are none. Value shape: literal numeric range 0..480 across 222 macros; 7 alias
or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_QCOM_RPMHPD_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Generic RPMH Power Domain Indexes`, `RPMh Power Domain performance levels`, `SA8775P Power Domain
Indexes`, `SDM670 Power Domain Indexes`, `SDM845 Power Domain Indexes`, `SDX55 Power Domain
Indexes`, `SDX65 Power Domain Indexes`, `SM6350 Power Domain Indexes`, `SM8150 Power Domain
Indexes`, `SA8155P is a special case, kept for backwards compatibility`, `SM8250 Power Domain
Indexes`, `SM8350 Power Domain Indexes`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 281 lines long. Notable source comments include `Generic RPMH Power Domain Indexes`,
`RPMh Power Domain performance levels`, `Platform-specific power domain bindings. Don't add new
entries here, use RPMHPD_* above.`, `SA8775P Power Domain Indexes`, `SDM670 Power Domain Indexes`,
`SDM845 Power Domain Indexes`. Example value clusters are RPMH: `RPMH_REGULATOR_LEVEL_RETENTION=16`,
`RPMH_REGULATOR_LEVEL_MIN_SVS=48`, `RPMH_REGULATOR_LEVEL_LOW_SVS_D3_0=49`,
`RPMH_REGULATOR_LEVEL_LOW_SVS_D3=50`; RPMHPD: `RPMHPD_CX=0`, `RPMHPD_CX_AO=1`, `RPMHPD_EBI=2`,
`RPMHPD_GFX=3`; SA8775P: `SA8775P_CX=0`, `SA8775P_CX_AO=1`, `SA8775P_DDR=2`, `SA8775P_EBI=3`;
SC8280XP: `SC8280XP_CX=0`, `SC8280XP_CX_AO=1`, `SC8280XP_DDR=2`, `SC8280XP_EBI=3`; SM8550:
`SM8550_CX=0`, `SM8550_CX_AO=1`, `SM8550_EBI=2`, `SM8550_GFX=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RPMHPD_CX`, `RPMHPD_CX_AO`, `RPMHPD_EBI`, `RPMHPD_GFX`, `RPMHPD_LCX`, `RPMHPD_LMX`, `RPMHPD_MMCX`,
`RPMHPD_MMCX_AO`. Test signals include dt_binding_check, boot-time genpd attachment, power-domain
on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/qcom,rpmhpd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/qcom-rpmpd.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/qcom-rpmpd.h

Purpose: `qcom-rpmpd.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 156 `#define`s covering power-domain IDs, power-
gate IDs, or performance-state constants. The main macro families are RPM_SMD (12), RPMPD (11),
MSM8998 (10), SDM660 (10), SM6375 (10), MSM8939 (8), QCM2290 (8), SM6115 (8), MSM8953 (7), MSM8994
(7). Representative constants are `RPMPD_VDDCX`, `RPMPD_VDDCX_AO`, `RPMPD_VDDCX_VFC`,
`RPMPD_VDDCX_VFL`, `RPMPD_VDDMX`, `RPMPD_VDDMX_AO`, `RPMPD_VDDMX_VFL`, `RPMPD_SSCCX`, `...`,
`RPM_SMD_LEVEL_SVS`, `RPM_SMD_LEVEL_SVS_PLUS`, `RPM_SMD_LEVEL_NOM`, `RPM_SMD_LEVEL_NOM_PLUS`,
`RPM_SMD_LEVEL_TURBO`, `RPM_SMD_LEVEL_TURBO_NO_CPR`, `RPM_SMD_LEVEL_TURBO_HIGH`,
`RPM_SMD_LEVEL_BINNING`. Function-like helpers are none. Value shape: literal numeric range 0..512
across 90 macros; 66 alias or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_QCOM_RPMPD_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Generic RPM Power Domain Indexes`, `VFC and VFL are mutually exclusive and can not be present on
the same platform`, `MDM9607 Power Domains`, `MSM8226 Power Domain Indexes`, `MSM8939 Power
Domains`, `MSM8916 Power Domain Indexes`, `MSM8909 Power Domain Indexes`, `MSM8917 Power Domain
Indexes`, `MSM8937 Power Domain Indexes`, `QM215 Power Domain Indexes`, `MSM8953 Power Domain
Indexes`, `MSM8974 Power Domain Indexes`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are `dt-bindings/power/qcom,rpmhpd.h`. Integration points are generic power-domain
providers, device `power-domains` phandles, OPP/performance-state users, and SoC power-controller
drivers.

Local source signals: The file is 215 lines long. Notable source comments include `Generic RPM Power Domain Indexes`, `VFC
and VFL are mutually exclusive and can not be present on the same platform`, `Platform-specific
power domain bindings. Don't add new entries here, use RPMPD_* above.`, `MDM9607 Power Domains`,
`MSM8226 Power Domain Indexes`, `MSM8939 Power Domains`. Example value clusters are RPM_SMD:
`RPM_SMD_LEVEL_RETENTION=16`, `RPM_SMD_LEVEL_RETENTION_PLUS=32`, `RPM_SMD_LEVEL_MIN_SVS=48`,
`RPM_SMD_LEVEL_LOW_SVS=64`; RPMPD: `RPMPD_VDDCX=0`, `RPMPD_VDDCX_AO=1`, `RPMPD_VDDCX_VFC=2`,
`RPMPD_VDDCX_VFL=2`; MSM8998: `MSM8998_VDDCX=RPMPD_VDDCX`, `MSM8998_VDDCX_AO=RPMPD_VDDCX_AO`,
`MSM8998_VDDCX_VFL=RPMPD_VDDCX_VFL`, `MSM8998_VDDMX=RPMPD_VDDMX`; SDM660:
`SDM660_VDDCX=RPMPD_VDDCX`, `SDM660_VDDCX_AO=RPMPD_VDDCX_AO`, `SDM660_VDDCX_VFL=RPMPD_VDDCX_VFL`,
`SDM660_VDDMX=RPMPD_VDDMX`; SM6375: `SM6375_VDDCX=0`, `SM6375_VDDCX_AO=1`, `SM6375_VDDCX_VFL=2`,
`SM6375_VDDMX=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RPMPD_VDDCX`, `RPMPD_VDDCX_AO`, `RPMPD_VDDCX_VFC`, `RPMPD_VDDCX_VFL`, `RPMPD_VDDMX`,
`RPMPD_VDDMX_AO`, `RPMPD_VDDMX_VFL`, `RPMPD_SSCCX`. Test signals include dt_binding_check, boot-time
genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/qcom-rpmpd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7742-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7742-sysc.h

Purpose: `r8a7742-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 12 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7742 (12). Representative
constants are `R8A7742_PD_CA15_CPU0`, `R8A7742_PD_CA15_CPU1`, `R8A7742_PD_CA15_CPU2`,
`R8A7742_PD_CA15_CPU3`, `R8A7742_PD_CA7_CPU0`, `R8A7742_PD_CA7_CPU1`, `R8A7742_PD_CA7_CPU2`,
`R8A7742_PD_CA7_CPU3`, `R8A7742_PD_CA7_CPU0`, `R8A7742_PD_CA7_CPU1`, `R8A7742_PD_CA7_CPU2`,
`R8A7742_PD_CA7_CPU3`, `R8A7742_PD_CA15_SCU`, `R8A7742_PD_RGX`, `R8A7742_PD_CA7_SCU`,
`R8A7742_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 12 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7742_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 29 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7742_SYSC_H__`. Example value clusters are R8A7742:
`R8A7742_PD_CA15_CPU0=0`, `R8A7742_PD_CA15_CPU1=1`, `R8A7742_PD_CA15_CPU2=2`,
`R8A7742_PD_CA15_CPU3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7742_PD_CA15_CPU0`, `R8A7742_PD_CA15_CPU1`, `R8A7742_PD_CA15_CPU2`, `R8A7742_PD_CA15_CPU3`,
`R8A7742_PD_CA7_CPU0`, `R8A7742_PD_CA7_CPU1`, `R8A7742_PD_CA7_CPU2`, `R8A7742_PD_CA7_CPU3`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7742-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7743-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7743-sysc.h

Purpose: `r8a7743-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7743 (5). Representative
constants are `R8A7743_PD_CA15_CPU0`, `R8A7743_PD_CA15_CPU1`, `R8A7743_PD_CA15_SCU`,
`R8A7743_PD_SGX`, `R8A7743_PD_ALWAYS_ON`, `R8A7743_PD_CA15_CPU0`, `R8A7743_PD_CA15_CPU1`,
`R8A7743_PD_CA15_SCU`, `R8A7743_PD_SGX`, `R8A7743_PD_ALWAYS_ON`. Function-like helpers are none.
Value shape: literal numeric range 0..32 across 5 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7743_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 22 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7743_SYSC_H__`. Example value clusters are R8A7743:
`R8A7743_PD_CA15_CPU0=0`, `R8A7743_PD_CA15_CPU1=1`, `R8A7743_PD_CA15_SCU=12`, `R8A7743_PD_SGX=20`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7743_PD_CA15_CPU0`, `R8A7743_PD_CA15_CPU1`, `R8A7743_PD_CA15_SCU`, `R8A7743_PD_SGX`,
`R8A7743_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd attachment, power-
domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7743-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7744-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7744-sysc.h

Purpose: `r8a7744-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7744 (5). Representative
constants are `R8A7744_PD_CA15_CPU0`, `R8A7744_PD_CA15_CPU1`, `R8A7744_PD_CA15_SCU`,
`R8A7744_PD_SGX`, `R8A7744_PD_ALWAYS_ON`, `R8A7744_PD_CA15_CPU0`, `R8A7744_PD_CA15_CPU1`,
`R8A7744_PD_CA15_SCU`, `R8A7744_PD_SGX`, `R8A7744_PD_ALWAYS_ON`. Function-like helpers are none.
Value shape: literal numeric range 0..32 across 5 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7744_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 24 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register) Note that RZ/G1N is identical to RZ/G2M w.r.t. power domains.`,
`Always-on power area`, `__DT_BINDINGS_POWER_R8A7744_SYSC_H__`. Example value clusters are R8A7744:
`R8A7744_PD_CA15_CPU0=0`, `R8A7744_PD_CA15_CPU1=1`, `R8A7744_PD_CA15_SCU=12`, `R8A7744_PD_SGX=20`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7744_PD_CA15_CPU0`, `R8A7744_PD_CA15_CPU1`, `R8A7744_PD_CA15_SCU`, `R8A7744_PD_SGX`,
`R8A7744_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd attachment, power-
domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7744-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7745-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7745-sysc.h

Purpose: `r8a7745-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7745 (5). Representative
constants are `R8A7745_PD_CA7_CPU0`, `R8A7745_PD_CA7_CPU1`, `R8A7745_PD_SGX`, `R8A7745_PD_CA7_SCU`,
`R8A7745_PD_ALWAYS_ON`, `R8A7745_PD_CA7_CPU0`, `R8A7745_PD_CA7_CPU1`, `R8A7745_PD_SGX`,
`R8A7745_PD_CA7_SCU`, `R8A7745_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal
numeric range 5..32 across 5 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7745_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 22 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7745_SYSC_H__`. Example value clusters are R8A7745: `R8A7745_PD_CA7_CPU0=5`,
`R8A7745_PD_CA7_CPU1=6`, `R8A7745_PD_SGX=20`, `R8A7745_PD_CA7_SCU=21`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7745_PD_CA7_CPU0`, `R8A7745_PD_CA7_CPU1`, `R8A7745_PD_SGX`, `R8A7745_PD_CA7_SCU`,
`R8A7745_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd attachment, power-
domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7745-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77470-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77470-sysc.h

Purpose: `r8a77470-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A77470 (5). Representative
constants are `R8A77470_PD_CA7_CPU0`, `R8A77470_PD_CA7_CPU1`, `R8A77470_PD_SGX`,
`R8A77470_PD_CA7_SCU`, `R8A77470_PD_ALWAYS_ON`, `R8A77470_PD_CA7_CPU0`, `R8A77470_PD_CA7_CPU1`,
`R8A77470_PD_SGX`, `R8A77470_PD_CA7_SCU`, `R8A77470_PD_ALWAYS_ON`. Function-like helpers are none.
Value shape: literal numeric range 5..32 across 5 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A77470_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 22 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A77470_SYSC_H__`. Example value clusters are R8A77470:
`R8A77470_PD_CA7_CPU0=5`, `R8A77470_PD_CA7_CPU1=6`, `R8A77470_PD_SGX=20`, `R8A77470_PD_CA7_SCU=21`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A77470_PD_CA7_CPU0`, `R8A77470_PD_CA7_CPU1`, `R8A77470_PD_SGX`, `R8A77470_PD_CA7_SCU`,
`R8A77470_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd attachment, power-
domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77470-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774a1-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774a1-sysc.h

Purpose: `r8a774a1-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 14 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A774A1 (14). Representative
constants are `R8A774A1_PD_CA57_CPU0`, `R8A774A1_PD_CA57_CPU1`, `R8A774A1_PD_CA53_CPU0`,
`R8A774A1_PD_CA53_CPU1`, `R8A774A1_PD_CA53_CPU2`, `R8A774A1_PD_CA53_CPU3`, `R8A774A1_PD_CA57_SCU`,
`R8A774A1_PD_A3VC`, `R8A774A1_PD_CA57_SCU`, `R8A774A1_PD_A3VC`, `R8A774A1_PD_3DG_A`,
`R8A774A1_PD_3DG_B`, `R8A774A1_PD_CA53_SCU`, `R8A774A1_PD_A2VC0`, `R8A774A1_PD_A2VC1`,
`R8A774A1_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 14 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A774A1_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 31 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A774A1_SYSC_H__`. Example value clusters are R8A774A1:
`R8A774A1_PD_CA57_CPU0=0`, `R8A774A1_PD_CA57_CPU1=1`, `R8A774A1_PD_CA53_CPU0=5`,
`R8A774A1_PD_CA53_CPU1=6`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A774A1_PD_CA57_CPU0`, `R8A774A1_PD_CA57_CPU1`, `R8A774A1_PD_CA53_CPU0`, `R8A774A1_PD_CA53_CPU1`,
`R8A774A1_PD_CA53_CPU2`, `R8A774A1_PD_CA53_CPU3`, `R8A774A1_PD_CA57_SCU`, `R8A774A1_PD_A3VC`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774a1-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774b1-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774b1-sysc.h

Purpose: `r8a774b1-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A774B1 (9). Representative
constants are `R8A774B1_PD_CA57_CPU0`, `R8A774B1_PD_CA57_CPU1`, `R8A774B1_PD_A3VP`,
`R8A774B1_PD_CA57_SCU`, `R8A774B1_PD_A3VC`, `R8A774B1_PD_3DG_A`, `R8A774B1_PD_3DG_B`,
`R8A774B1_PD_A2VC1`, `R8A774B1_PD_CA57_CPU1`, `R8A774B1_PD_A3VP`, `R8A774B1_PD_CA57_SCU`,
`R8A774B1_PD_A3VC`, `R8A774B1_PD_3DG_A`, `R8A774B1_PD_3DG_B`, `R8A774B1_PD_A2VC1`,
`R8A774B1_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A774B1_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 26 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A774B1_SYSC_H__`. Example value clusters are R8A774B1:
`R8A774B1_PD_CA57_CPU0=0`, `R8A774B1_PD_CA57_CPU1=1`, `R8A774B1_PD_A3VP=9`,
`R8A774B1_PD_CA57_SCU=12`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A774B1_PD_CA57_CPU0`, `R8A774B1_PD_CA57_CPU1`, `R8A774B1_PD_A3VP`, `R8A774B1_PD_CA57_SCU`,
`R8A774B1_PD_A3VC`, `R8A774B1_PD_3DG_A`, `R8A774B1_PD_3DG_B`, `R8A774B1_PD_A2VC1`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774b1-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774c0-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774c0-sysc.h

Purpose: `r8a774c0-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A774C0 (8). Representative
constants are `R8A774C0_PD_CA53_CPU0`, `R8A774C0_PD_CA53_CPU1`, `R8A774C0_PD_A3VC`,
`R8A774C0_PD_3DG_A`, `R8A774C0_PD_3DG_B`, `R8A774C0_PD_CA53_SCU`, `R8A774C0_PD_A2VC1`,
`R8A774C0_PD_ALWAYS_ON`, `R8A774C0_PD_CA53_CPU0`, `R8A774C0_PD_CA53_CPU1`, `R8A774C0_PD_A3VC`,
`R8A774C0_PD_3DG_A`, `R8A774C0_PD_3DG_B`, `R8A774C0_PD_CA53_SCU`, `R8A774C0_PD_A2VC1`,
`R8A774C0_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 5..32
across 8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A774C0_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 25 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A774C0_SYSC_H__`. Example value clusters are R8A774C0:
`R8A774C0_PD_CA53_CPU0=5`, `R8A774C0_PD_CA53_CPU1=6`, `R8A774C0_PD_A3VC=14`, `R8A774C0_PD_3DG_A=17`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A774C0_PD_CA53_CPU0`, `R8A774C0_PD_CA53_CPU1`, `R8A774C0_PD_A3VC`, `R8A774C0_PD_3DG_A`,
`R8A774C0_PD_3DG_B`, `R8A774C0_PD_CA53_SCU`, `R8A774C0_PD_A2VC1`, `R8A774C0_PD_ALWAYS_ON`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774c0-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774e1-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774e1-sysc.h

Purpose: `r8a774e1-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 19 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A774E1 (19). Representative
constants are `R8A774E1_PD_CA57_CPU0`, `R8A774E1_PD_CA57_CPU1`, `R8A774E1_PD_CA57_CPU2`,
`R8A774E1_PD_CA57_CPU3`, `R8A774E1_PD_CA53_CPU0`, `R8A774E1_PD_CA53_CPU1`, `R8A774E1_PD_CA53_CPU2`,
`R8A774E1_PD_CA53_CPU3`, `...`, `R8A774E1_PD_3DG_A`, `R8A774E1_PD_3DG_B`, `R8A774E1_PD_3DG_C`,
`R8A774E1_PD_3DG_D`, `R8A774E1_PD_CA53_SCU`, `R8A774E1_PD_3DG_E`, `R8A774E1_PD_A2VC1`,
`R8A774E1_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 19 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A774E1_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 36 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A774E1_SYSC_H__`. Example value clusters are R8A774E1:
`R8A774E1_PD_CA57_CPU0=0`, `R8A774E1_PD_CA57_CPU1=1`, `R8A774E1_PD_CA57_CPU2=2`,
`R8A774E1_PD_CA57_CPU3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A774E1_PD_CA57_CPU0`, `R8A774E1_PD_CA57_CPU1`, `R8A774E1_PD_CA57_CPU2`, `R8A774E1_PD_CA57_CPU3`,
`R8A774E1_PD_CA53_CPU0`, `R8A774E1_PD_CA53_CPU1`, `R8A774E1_PD_CA53_CPU2`, `R8A774E1_PD_CA53_CPU3`.
Test signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a774e1-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7779-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7779-sysc.h

Purpose: `r8a7779-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7779 (7). Representative
constants are `R8A7779_PD_ARM1`, `R8A7779_PD_ARM2`, `R8A7779_PD_ARM3`, `R8A7779_PD_SGX`,
`R8A7779_PD_VDP`, `R8A7779_PD_IMP`, `R8A7779_PD_ALWAYS_ON`, `R8A7779_PD_ARM1`, `R8A7779_PD_ARM2`,
`R8A7779_PD_ARM3`, `R8A7779_PD_SGX`, `R8A7779_PD_VDP`, `R8A7779_PD_IMP`, `R8A7779_PD_ALWAYS_ON`.
Function-like helpers are none. Value shape: literal numeric range 1..32 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7779_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 24 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7779_SYSC_H__`. Example value clusters are R8A7779: `R8A7779_PD_ARM1=1`,
`R8A7779_PD_ARM2=2`, `R8A7779_PD_ARM3=3`, `R8A7779_PD_SGX=20`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7779_PD_ARM1`, `R8A7779_PD_ARM2`, `R8A7779_PD_ARM3`, `R8A7779_PD_SGX`, `R8A7779_PD_VDP`,
`R8A7779_PD_IMP`, `R8A7779_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7779-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7790-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7790-sysc.h

Purpose: `r8a7790-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 14 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7790 (14). Representative
constants are `R8A7790_PD_CA15_CPU0`, `R8A7790_PD_CA15_CPU1`, `R8A7790_PD_CA15_CPU2`,
`R8A7790_PD_CA15_CPU3`, `R8A7790_PD_CA7_CPU0`, `R8A7790_PD_CA7_CPU1`, `R8A7790_PD_CA7_CPU2`,
`R8A7790_PD_CA7_CPU3`, `R8A7790_PD_CA7_CPU2`, `R8A7790_PD_CA7_CPU3`, `R8A7790_PD_CA15_SCU`,
`R8A7790_PD_SH_4A`, `R8A7790_PD_RGX`, `R8A7790_PD_CA7_SCU`, `R8A7790_PD_IMP`,
`R8A7790_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 14 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7790_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 31 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7790_SYSC_H__`. Example value clusters are R8A7790:
`R8A7790_PD_CA15_CPU0=0`, `R8A7790_PD_CA15_CPU1=1`, `R8A7790_PD_CA15_CPU2=2`,
`R8A7790_PD_CA15_CPU3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7790_PD_CA15_CPU0`, `R8A7790_PD_CA15_CPU1`, `R8A7790_PD_CA15_CPU2`, `R8A7790_PD_CA15_CPU3`,
`R8A7790_PD_CA7_CPU0`, `R8A7790_PD_CA7_CPU1`, `R8A7790_PD_CA7_CPU2`, `R8A7790_PD_CA7_CPU3`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7790-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7791-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7791-sysc.h

Purpose: `r8a7791-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7791 (6). Representative
constants are `R8A7791_PD_CA15_CPU0`, `R8A7791_PD_CA15_CPU1`, `R8A7791_PD_CA15_SCU`,
`R8A7791_PD_SH_4A`, `R8A7791_PD_SGX`, `R8A7791_PD_ALWAYS_ON`, `R8A7791_PD_CA15_CPU0`,
`R8A7791_PD_CA15_CPU1`, `R8A7791_PD_CA15_SCU`, `R8A7791_PD_SH_4A`, `R8A7791_PD_SGX`,
`R8A7791_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7791_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 23 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7791_SYSC_H__`. Example value clusters are R8A7791:
`R8A7791_PD_CA15_CPU0=0`, `R8A7791_PD_CA15_CPU1=1`, `R8A7791_PD_CA15_SCU=12`, `R8A7791_PD_SH_4A=16`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7791_PD_CA15_CPU0`, `R8A7791_PD_CA15_CPU1`, `R8A7791_PD_CA15_SCU`, `R8A7791_PD_SH_4A`,
`R8A7791_PD_SGX`, `R8A7791_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7791-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7792-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7792-sysc.h

Purpose: `r8a7792-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7792 (6). Representative
constants are `R8A7792_PD_CA15_CPU0`, `R8A7792_PD_CA15_CPU1`, `R8A7792_PD_CA15_SCU`,
`R8A7792_PD_SGX`, `R8A7792_PD_IMP`, `R8A7792_PD_ALWAYS_ON`, `R8A7792_PD_CA15_CPU0`,
`R8A7792_PD_CA15_CPU1`, `R8A7792_PD_CA15_SCU`, `R8A7792_PD_SGX`, `R8A7792_PD_IMP`,
`R8A7792_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7792_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 23 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7792_SYSC_H__`. Example value clusters are R8A7792:
`R8A7792_PD_CA15_CPU0=0`, `R8A7792_PD_CA15_CPU1=1`, `R8A7792_PD_CA15_SCU=12`, `R8A7792_PD_SGX=20`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7792_PD_CA15_CPU0`, `R8A7792_PD_CA15_CPU1`, `R8A7792_PD_CA15_SCU`, `R8A7792_PD_SGX`,
`R8A7792_PD_IMP`, `R8A7792_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7792-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7793-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7793-sysc.h

Purpose: `r8a7793-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7793 (6). Representative
constants are `R8A7793_PD_CA15_CPU0`, `R8A7793_PD_CA15_CPU1`, `R8A7793_PD_CA15_SCU`,
`R8A7793_PD_SH_4A`, `R8A7793_PD_SGX`, `R8A7793_PD_ALWAYS_ON`, `R8A7793_PD_CA15_CPU0`,
`R8A7793_PD_CA15_CPU1`, `R8A7793_PD_CA15_SCU`, `R8A7793_PD_SH_4A`, `R8A7793_PD_SGX`,
`R8A7793_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7793_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 25 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register) Note that R-Car M2-N is identical to R-Car M2-W w.r.t. power
domains.`, `Always-on power area`, `__DT_BINDINGS_POWER_R8A7793_SYSC_H__`. Example value clusters
are R8A7793: `R8A7793_PD_CA15_CPU0=0`, `R8A7793_PD_CA15_CPU1=1`, `R8A7793_PD_CA15_SCU=12`,
`R8A7793_PD_SH_4A=16`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7793_PD_CA15_CPU0`, `R8A7793_PD_CA15_CPU1`, `R8A7793_PD_CA15_SCU`, `R8A7793_PD_SH_4A`,
`R8A7793_PD_SGX`, `R8A7793_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7793-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7794-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7794-sysc.h

Purpose: `r8a7794-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7794 (6). Representative
constants are `R8A7794_PD_CA7_CPU0`, `R8A7794_PD_CA7_CPU1`, `R8A7794_PD_SH_4A`, `R8A7794_PD_SGX`,
`R8A7794_PD_CA7_SCU`, `R8A7794_PD_ALWAYS_ON`, `R8A7794_PD_CA7_CPU0`, `R8A7794_PD_CA7_CPU1`,
`R8A7794_PD_SH_4A`, `R8A7794_PD_SGX`, `R8A7794_PD_CA7_SCU`, `R8A7794_PD_ALWAYS_ON`. Function-like
helpers are none. Value shape: literal numeric range 5..32 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7794_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 23 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7794_SYSC_H__`. Example value clusters are R8A7794: `R8A7794_PD_CA7_CPU0=5`,
`R8A7794_PD_CA7_CPU1=6`, `R8A7794_PD_SH_4A=16`, `R8A7794_PD_SGX=20`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7794_PD_CA7_CPU0`, `R8A7794_PD_CA7_CPU1`, `R8A7794_PD_SH_4A`, `R8A7794_PD_SGX`,
`R8A7794_PD_CA7_SCU`, `R8A7794_PD_ALWAYS_ON`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7794-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7795-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7795-sysc.h

Purpose: `r8a7795-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 21 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7795 (21). Representative
constants are `R8A7795_PD_CA57_CPU0`, `R8A7795_PD_CA57_CPU1`, `R8A7795_PD_CA57_CPU2`,
`R8A7795_PD_CA57_CPU3`, `R8A7795_PD_CA53_CPU0`, `R8A7795_PD_CA53_CPU1`, `R8A7795_PD_CA53_CPU2`,
`R8A7795_PD_CA53_CPU3`, `...`, `R8A7795_PD_3DG_B`, `R8A7795_PD_3DG_C`, `R8A7795_PD_3DG_D`,
`R8A7795_PD_CA53_SCU`, `R8A7795_PD_3DG_E`, `R8A7795_PD_A3IR`, `R8A7795_PD_A2VC1`,
`R8A7795_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 21 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7795_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 38 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7795_SYSC_H__`. Example value clusters are R8A7795:
`R8A7795_PD_CA57_CPU0=0`, `R8A7795_PD_CA57_CPU1=1`, `R8A7795_PD_CA57_CPU2=2`,
`R8A7795_PD_CA57_CPU3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7795_PD_CA57_CPU0`, `R8A7795_PD_CA57_CPU1`, `R8A7795_PD_CA57_CPU2`, `R8A7795_PD_CA57_CPU3`,
`R8A7795_PD_CA53_CPU0`, `R8A7795_PD_CA53_CPU1`, `R8A7795_PD_CA53_CPU2`, `R8A7795_PD_CA53_CPU3`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7795-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7796-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7796-sysc.h

Purpose: `r8a7796-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 16 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A7796 (16). Representative
constants are `R8A7796_PD_CA57_CPU0`, `R8A7796_PD_CA57_CPU1`, `R8A7796_PD_CA53_CPU0`,
`R8A7796_PD_CA53_CPU1`, `R8A7796_PD_CA53_CPU2`, `R8A7796_PD_CA53_CPU3`, `R8A7796_PD_CA57_SCU`,
`R8A7796_PD_CR7`, `R8A7796_PD_A3VC`, `R8A7796_PD_3DG_A`, `R8A7796_PD_3DG_B`, `R8A7796_PD_CA53_SCU`,
`R8A7796_PD_A3IR`, `R8A7796_PD_A2VC0`, `R8A7796_PD_A2VC1`, `R8A7796_PD_ALWAYS_ON`. Function-like
helpers are none. Value shape: literal numeric range 0..32 across 16 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A7796_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 33 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A7796_SYSC_H__`. Example value clusters are R8A7796:
`R8A7796_PD_CA57_CPU0=0`, `R8A7796_PD_CA57_CPU1=1`, `R8A7796_PD_CA53_CPU0=5`,
`R8A7796_PD_CA53_CPU1=6`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A7796_PD_CA57_CPU0`, `R8A7796_PD_CA57_CPU1`, `R8A7796_PD_CA53_CPU0`, `R8A7796_PD_CA53_CPU1`,
`R8A7796_PD_CA53_CPU2`, `R8A7796_PD_CA53_CPU3`, `R8A7796_PD_CA57_SCU`, `R8A7796_PD_CR7`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a7796-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77961-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77961-sysc.h

Purpose: `r8a77961-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 15 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A77961 (15). Representative
constants are `R8A77961_PD_CA57_CPU0`, `R8A77961_PD_CA57_CPU1`, `R8A77961_PD_CA53_CPU0`,
`R8A77961_PD_CA53_CPU1`, `R8A77961_PD_CA53_CPU2`, `R8A77961_PD_CA53_CPU3`, `R8A77961_PD_CA57_SCU`,
`R8A77961_PD_CR7`, `R8A77961_PD_CR7`, `R8A77961_PD_A3VC`, `R8A77961_PD_3DG_A`, `R8A77961_PD_3DG_B`,
`R8A77961_PD_CA53_SCU`, `R8A77961_PD_A3IR`, `R8A77961_PD_A2VC1`, `R8A77961_PD_ALWAYS_ON`. Function-
like helpers are none. Value shape: literal numeric range 0..32 across 15 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A77961_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 32 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A77961_SYSC_H__`. Example value clusters are R8A77961:
`R8A77961_PD_CA57_CPU0=0`, `R8A77961_PD_CA57_CPU1=1`, `R8A77961_PD_CA53_CPU0=5`,
`R8A77961_PD_CA53_CPU1=6`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A77961_PD_CA57_CPU0`, `R8A77961_PD_CA57_CPU1`, `R8A77961_PD_CA53_CPU0`, `R8A77961_PD_CA53_CPU1`,
`R8A77961_PD_CA53_CPU2`, `R8A77961_PD_CA53_CPU3`, `R8A77961_PD_CA57_SCU`, `R8A77961_PD_CR7`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77961-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77965-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77965-sysc.h

Purpose: `r8a77965-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 10 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A77965 (10). Representative
constants are `R8A77965_PD_CA57_CPU0`, `R8A77965_PD_CA57_CPU1`, `R8A77965_PD_A3VP`,
`R8A77965_PD_CA57_SCU`, `R8A77965_PD_CR7`, `R8A77965_PD_A3VC`, `R8A77965_PD_3DG_A`,
`R8A77965_PD_3DG_B`, `R8A77965_PD_A3VP`, `R8A77965_PD_CA57_SCU`, `R8A77965_PD_CR7`,
`R8A77965_PD_A3VC`, `R8A77965_PD_3DG_A`, `R8A77965_PD_3DG_B`, `R8A77965_PD_A2VC1`,
`R8A77965_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..32
across 10 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A77965_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 29 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A77965_SYSC_H__`. Example value clusters are R8A77965:
`R8A77965_PD_CA57_CPU0=0`, `R8A77965_PD_CA57_CPU1=1`, `R8A77965_PD_A3VP=9`,
`R8A77965_PD_CA57_SCU=12`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A77965_PD_CA57_CPU0`, `R8A77965_PD_CA57_CPU1`, `R8A77965_PD_A3VP`, `R8A77965_PD_CA57_SCU`,
`R8A77965_PD_CR7`, `R8A77965_PD_A3VC`, `R8A77965_PD_3DG_A`, `R8A77965_PD_3DG_B`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77965-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77970-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77970-sysc.h

Purpose: `r8a77970-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A77970 (11). Representative
constants are `R8A77970_PD_CA53_CPU0`, `R8A77970_PD_CA53_CPU1`, `R8A77970_PD_CA53_SCU`,
`R8A77970_PD_A2IR0`, `R8A77970_PD_A3IR`, `R8A77970_PD_A2IR1`, `R8A77970_PD_A2DP`,
`R8A77970_PD_A2CN`, `R8A77970_PD_A2IR0`, `R8A77970_PD_A3IR`, `R8A77970_PD_A2IR1`,
`R8A77970_PD_A2DP`, `R8A77970_PD_A2CN`, `R8A77970_PD_A2SC0`, `R8A77970_PD_A2SC1`,
`R8A77970_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 5..32
across 11 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A77970_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 28 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A77970_SYSC_H__`. Example value clusters are R8A77970:
`R8A77970_PD_CA53_CPU0=5`, `R8A77970_PD_CA53_CPU1=6`, `R8A77970_PD_CA53_SCU=21`,
`R8A77970_PD_A2IR0=23`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A77970_PD_CA53_CPU0`, `R8A77970_PD_CA53_CPU1`, `R8A77970_PD_CA53_SCU`, `R8A77970_PD_A2IR0`,
`R8A77970_PD_A3IR`, `R8A77970_PD_A2IR1`, `R8A77970_PD_A2DP`, `R8A77970_PD_A2CN`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77970-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77980-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77980-sysc.h

Purpose: `r8a77980-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 25 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A77980 (25). Representative
constants are `R8A77980_PD_A2SC2`, `R8A77980_PD_A2SC3`, `R8A77980_PD_A2SC4`, `R8A77980_PD_A2DP0`,
`R8A77980_PD_A2DP1`, `R8A77980_PD_CA53_CPU0`, `R8A77980_PD_CA53_CPU1`, `R8A77980_PD_CA53_CPU2`,
`...`, `R8A77980_PD_A3VIP1`, `R8A77980_PD_A3VIP2`, `R8A77980_PD_A2IR1`, `R8A77980_PD_A2IR2`,
`R8A77980_PD_A2IR3`, `R8A77980_PD_A2SC0`, `R8A77980_PD_A2SC1`, `R8A77980_PD_ALWAYS_ON`. Function-
like helpers are none. Value shape: literal numeric range 0..32 across 25 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A77980_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 43 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A77980_SYSC_H__`. Example value clusters are R8A77980: `R8A77980_PD_A2SC2=0`,
`R8A77980_PD_A2SC3=1`, `R8A77980_PD_A2SC4=2`, `R8A77980_PD_A2DP0=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A77980_PD_A2SC2`, `R8A77980_PD_A2SC3`, `R8A77980_PD_A2SC4`, `R8A77980_PD_A2DP0`,
`R8A77980_PD_A2DP1`, `R8A77980_PD_CA53_CPU0`, `R8A77980_PD_CA53_CPU1`, `R8A77980_PD_CA53_CPU2`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77980-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77990-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77990-sysc.h

Purpose: `r8a77990-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A77990 (9). Representative
constants are `R8A77990_PD_CA53_CPU0`, `R8A77990_PD_CA53_CPU1`, `R8A77990_PD_CR7`,
`R8A77990_PD_A3VC`, `R8A77990_PD_3DG_A`, `R8A77990_PD_3DG_B`, `R8A77990_PD_CA53_SCU`,
`R8A77990_PD_A2VC1`, `R8A77990_PD_CA53_CPU1`, `R8A77990_PD_CR7`, `R8A77990_PD_A3VC`,
`R8A77990_PD_3DG_A`, `R8A77990_PD_3DG_B`, `R8A77990_PD_CA53_SCU`, `R8A77990_PD_A2VC1`,
`R8A77990_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 5..32
across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A77990_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 26 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A77990_SYSC_H__`. Example value clusters are R8A77990:
`R8A77990_PD_CA53_CPU0=5`, `R8A77990_PD_CA53_CPU1=6`, `R8A77990_PD_CR7=13`, `R8A77990_PD_A3VC=14`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A77990_PD_CA53_CPU0`, `R8A77990_PD_CA53_CPU1`, `R8A77990_PD_CR7`, `R8A77990_PD_A3VC`,
`R8A77990_PD_3DG_A`, `R8A77990_PD_3DG_B`, `R8A77990_PD_CA53_SCU`, `R8A77990_PD_A2VC1`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77990-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77995-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77995-sysc.h

Purpose: `r8a77995-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A77995 (3). Representative
constants are `R8A77995_PD_CA53_CPU0`, `R8A77995_PD_CA53_SCU`, `R8A77995_PD_ALWAYS_ON`,
`R8A77995_PD_CA53_CPU0`, `R8A77995_PD_CA53_SCU`, `R8A77995_PD_ALWAYS_ON`. Function-like helpers are
none. Value shape: literal numeric range 5..32 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A77995_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 20 lines long. Notable source comments include `These power domain indices match the
numbers of the interrupt bits representing the power areas in the various Interrupt Registers (e.g.
SYSCISR, Interrupt Status Register)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A77995_SYSC_H__`. Example value clusters are R8A77995:
`R8A77995_PD_CA53_CPU0=5`, `R8A77995_PD_CA53_SCU=21`, `R8A77995_PD_ALWAYS_ON=32`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A77995_PD_CA53_CPU0`, `R8A77995_PD_CA53_SCU`, `R8A77995_PD_ALWAYS_ON`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a77995-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a779a0-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a779a0-sysc.h

Purpose: `r8a779a0-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 44 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A779A0 (44). Representative
constants are `R8A779A0_PD_A1E0D0C0`, `R8A779A0_PD_A1E0D0C1`, `R8A779A0_PD_A1E0D1C0`,
`R8A779A0_PD_A1E0D1C1`, `R8A779A0_PD_A1E1D0C0`, `R8A779A0_PD_A1E1D0C1`, `R8A779A0_PD_A1E1D1C0`,
`R8A779A0_PD_A1E1D1C1`, `...`, `R8A779A0_PD_A2CN1`, `R8A779A0_PD_A3VIP0`, `R8A779A0_PD_A3VIP1`,
`R8A779A0_PD_A3VIP2`, `R8A779A0_PD_A3VIP3`, `R8A779A0_PD_A3ISP01`, `R8A779A0_PD_A3ISP23`,
`R8A779A0_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..64
across 44 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A779A0_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 59 lines long. Notable source comments include `These power domain indices match the
Power Domain Register Numbers (PDR)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A779A0_SYSC_H__`. Example value clusters are R8A779A0:
`R8A779A0_PD_A1E0D0C0=0`, `R8A779A0_PD_A1E0D0C1=1`, `R8A779A0_PD_A1E0D1C0=2`,
`R8A779A0_PD_A1E0D1C1=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A779A0_PD_A1E0D0C0`, `R8A779A0_PD_A1E0D0C1`, `R8A779A0_PD_A1E0D1C0`, `R8A779A0_PD_A1E0D1C1`,
`R8A779A0_PD_A1E1D0C0`, `R8A779A0_PD_A1E1D0C1`, `R8A779A0_PD_A1E1D1C0`, `R8A779A0_PD_A1E1D1C1`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a779a0-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a779f0-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a779f0-sysc.h

Purpose: `r8a779f0-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 15 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A779F0 (15). Representative
constants are `R8A779F0_PD_A1E0D0C0`, `R8A779F0_PD_A1E0D0C1`, `R8A779F0_PD_A1E0D1C0`,
`R8A779F0_PD_A1E0D1C1`, `R8A779F0_PD_A1E1D0C0`, `R8A779F0_PD_A1E1D0C1`, `R8A779F0_PD_A1E1D1C0`,
`R8A779F0_PD_A1E1D1C1`, `R8A779F0_PD_A1E1D1C1`, `R8A779F0_PD_A2E0D0`, `R8A779F0_PD_A2E0D1`,
`R8A779F0_PD_A2E1D0`, `R8A779F0_PD_A2E1D1`, `R8A779F0_PD_A3E0`, `R8A779F0_PD_A3E1`,
`R8A779F0_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..64
across 15 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A779F0_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 30 lines long. Notable source comments include `These power domain indices match the
Power Domain Register Numbers (PDR)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A779A0_SYSC_H__`. Example value clusters are R8A779F0:
`R8A779F0_PD_A1E0D0C0=0`, `R8A779F0_PD_A1E0D0C1=1`, `R8A779F0_PD_A1E0D1C0=2`,
`R8A779F0_PD_A1E0D1C1=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A779F0_PD_A1E0D0C0`, `R8A779F0_PD_A1E0D0C1`, `R8A779F0_PD_A1E0D1C0`, `R8A779F0_PD_A1E0D1C1`,
`R8A779F0_PD_A1E1D0C0`, `R8A779F0_PD_A1E1D0C1`, `R8A779F0_PD_A1E1D1C0`, `R8A779F0_PD_A1E1D1C1`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a779f0-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a779g0-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a779g0-sysc.h

Purpose: `r8a779g0-sysc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 31 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A779G0 (31). Representative
constants are `R8A779G0_PD_A1E0D0C0`, `R8A779G0_PD_A1E0D0C1`, `R8A779G0_PD_A1E0D1C0`,
`R8A779G0_PD_A1E0D1C1`, `R8A779G0_PD_A2E0D0`, `R8A779G0_PD_A2E0D1`, `R8A779G0_PD_A3E0`,
`R8A779G0_PD_A33DGA`, `...`, `R8A779G0_PD_A1DSP3`, `R8A779G0_PD_A3VIP0`, `R8A779G0_PD_A3VIP1`,
`R8A779G0_PD_A3VIP2`, `R8A779G0_PD_A3ISP0`, `R8A779G0_PD_A3ISP1`, `R8A779G0_PD_A3DUL`,
`R8A779G0_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..64
across 31 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_R8A779G0_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 46 lines long. Notable source comments include `These power domain indices match the
Power Domain Register Numbers (PDR)`, `Always-on power area`,
`__DT_BINDINGS_POWER_R8A779G0_SYSC_H__`. Example value clusters are R8A779G0:
`R8A779G0_PD_A1E0D0C0=0`, `R8A779G0_PD_A1E0D0C1=1`, `R8A779G0_PD_A1E0D1C0=2`,
`R8A779G0_PD_A1E0D1C1=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A779G0_PD_A1E0D0C0`, `R8A779G0_PD_A1E0D0C1`, `R8A779G0_PD_A1E0D1C0`, `R8A779G0_PD_A1E0D1C1`,
`R8A779G0_PD_A2E0D0`, `R8A779G0_PD_A2E0D1`, `R8A779G0_PD_A3E0`, `R8A779G0_PD_A33DGA`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/r8a779g0-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/raspberrypi-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/raspberrypi-power.h

Purpose: `raspberrypi-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 24 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RPI_POWER (24). Representative
constants are `RPI_POWER_DOMAIN_I2C0`, `RPI_POWER_DOMAIN_I2C1`, `RPI_POWER_DOMAIN_I2C2`,
`RPI_POWER_DOMAIN_VIDEO_SCALER`, `RPI_POWER_DOMAIN_VPU1`, `RPI_POWER_DOMAIN_HDMI`,
`RPI_POWER_DOMAIN_USB`, `RPI_POWER_DOMAIN_VEC`, `...`, `RPI_POWER_DOMAIN_CPI`,
`RPI_POWER_DOMAIN_DSI0`, `RPI_POWER_DOMAIN_DSI1`, `RPI_POWER_DOMAIN_TRANSPOSER`,
`RPI_POWER_DOMAIN_CCP2TX`, `RPI_POWER_DOMAIN_CDP`, `RPI_POWER_DOMAIN_ARM`, `RPI_POWER_DOMAIN_COUNT`.
Function-like helpers are none. Value shape: literal numeric range 0..23 across 24 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_ARM_BCM2835_RPI_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RPI_POWER group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 38 lines long. Notable source comments include `These power domain indices are the
firmware interface's indices minus one.`, `_DT_BINDINGS_ARM_BCM2835_RPI_POWER_H`. Example value
clusters are RPI_POWER: `RPI_POWER_DOMAIN_I2C0=0`, `RPI_POWER_DOMAIN_I2C1=1`,
`RPI_POWER_DOMAIN_I2C2=2`, `RPI_POWER_DOMAIN_VIDEO_SCALER=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RPI_POWER_DOMAIN_I2C0`, `RPI_POWER_DOMAIN_I2C1`, `RPI_POWER_DOMAIN_I2C2`,
`RPI_POWER_DOMAIN_VIDEO_SCALER`, `RPI_POWER_DOMAIN_VPU1`, `RPI_POWER_DOMAIN_HDMI`,
`RPI_POWER_DOMAIN_USB`, `RPI_POWER_DOMAIN_VEC`. Test signals include dt_binding_check, boot-time
genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/raspberrypi-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/renesas,r8a779h0-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/renesas,r8a779h0-sysc.h

Purpose: `renesas,r8a779h0-sysc.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 34 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are R8A779H0 (34). Representative
constants are `R8A779H0_PD_A1E0D0C0`, `R8A779H0_PD_A1E0D0C1`, `R8A779H0_PD_A1E0D0C2`,
`R8A779H0_PD_A1E0D0C3`, `R8A779H0_PD_A2E0D0`, `R8A779H0_PD_A3CR0`, `R8A779H0_PD_A3CR1`,
`R8A779H0_PD_A3CR2`, `...`, `R8A779H0_PD_A3IMR3`, `R8A779H0_PD_A3PCI`, `R8A779H0_PD_A2PCIPHY`,
`R8A779H0_PD_A3VIP0`, `R8A779H0_PD_A3VIP2`, `R8A779H0_PD_A3ISP0`, `R8A779H0_PD_A3DUL`,
`R8A779H0_PD_ALWAYS_ON`. Function-like helpers are none. Value shape: literal numeric range 0..64
across 34 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RENESAS_R8A779H0_SYSC_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `Always-on power area`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 49 lines long. Notable source comments include `These power domain indices match the
Power Domain Register Numbers (PDR)`, `Always-on power area`,
`__DT_BINDINGS_POWER_RENESAS_R8A779H0_SYSC_H__`. Example value clusters are R8A779H0:
`R8A779H0_PD_A1E0D0C0=0`, `R8A779H0_PD_A1E0D0C1=1`, `R8A779H0_PD_A1E0D0C2=2`,
`R8A779H0_PD_A1E0D0C3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`R8A779H0_PD_A1E0D0C0`, `R8A779H0_PD_A1E0D0C1`, `R8A779H0_PD_A1E0D0C2`, `R8A779H0_PD_A1E0D0C3`,
`R8A779H0_PD_A2E0D0`, `R8A779H0_PD_A3CR0`, `R8A779H0_PD_A3CR1`, `R8A779H0_PD_A3CR2`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/renesas,r8a779h0-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3036-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3036-power.h

Purpose: `rk3036-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3036 (7). Representative
constants are `RK3036_PD_MSCH`, `RK3036_PD_CORE`, `RK3036_PD_PERI`, `RK3036_PD_VIO`,
`RK3036_PD_VPU`, `RK3036_PD_GPU`, `RK3036_PD_SYS`, `RK3036_PD_MSCH`, `RK3036_PD_CORE`,
`RK3036_PD_PERI`, `RK3036_PD_VIO`, `RK3036_PD_VPU`, `RK3036_PD_GPU`, `RK3036_PD_SYS`. Function-like
helpers are none. Value shape: literal numeric range 0..6 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3036_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RK3036 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 13 lines long. Notable source comments include none. Example value clusters are RK3036:
`RK3036_PD_MSCH=0`, `RK3036_PD_CORE=1`, `RK3036_PD_PERI=2`, `RK3036_PD_VIO=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3036_PD_MSCH`, `RK3036_PD_CORE`, `RK3036_PD_PERI`, `RK3036_PD_VIO`, `RK3036_PD_VPU`,
`RK3036_PD_GPU`, `RK3036_PD_SYS`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3036-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3066-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3066-power.h

Purpose: `rk3066-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3066 (11). Representative
constants are `RK3066_PD_A9_0`, `RK3066_PD_A9_1`, `RK3066_PD_DBG`, `RK3066_PD_SCU`,
`RK3066_PD_VIDEO`, `RK3066_PD_VIO`, `RK3066_PD_GPU`, `RK3066_PD_PERI`, `RK3066_PD_SCU`,
`RK3066_PD_VIDEO`, `RK3066_PD_VIO`, `RK3066_PD_GPU`, `RK3066_PD_PERI`, `RK3066_PD_CPU`,
`RK3066_PD_ALIVE`, `RK3066_PD_RTC`. Function-like helpers are none. Value shape: literal numeric
range 0..12 across 11 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3066_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_LOGIC`, `VD_PMU`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 22 lines long. Notable source comments include `VD_CORE`, `VD_LOGIC`, `VD_PMU`. Example
value clusters are RK3066: `RK3066_PD_A9_0=0`, `RK3066_PD_A9_1=1`, `RK3066_PD_DBG=4`,
`RK3066_PD_SCU=5`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3066_PD_A9_0`, `RK3066_PD_A9_1`, `RK3066_PD_DBG`, `RK3066_PD_SCU`, `RK3066_PD_VIDEO`,
`RK3066_PD_VIO`, `RK3066_PD_GPU`, `RK3066_PD_PERI`. Test signals include dt_binding_check, boot-time
genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3066-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3128-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3128-power.h

Purpose: `rk3128-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3128 (5). Representative
constants are `RK3128_PD_CORE`, `RK3128_PD_VIO`, `RK3128_PD_VIDEO`, `RK3128_PD_GPU`,
`RK3128_PD_MSCH`, `RK3128_PD_CORE`, `RK3128_PD_VIO`, `RK3128_PD_VIDEO`, `RK3128_PD_GPU`,
`RK3128_PD_MSCH`. Function-like helpers are none. Value shape: literal numeric range 0..4 across 5
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3128_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_LOGIC`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 14 lines long. Notable source comments include `VD_CORE`, `VD_LOGIC`. Example value
clusters are RK3128: `RK3128_PD_CORE=0`, `RK3128_PD_VIO=1`, `RK3128_PD_VIDEO=2`, `RK3128_PD_GPU=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3128_PD_CORE`, `RK3128_PD_VIO`, `RK3128_PD_VIDEO`, `RK3128_PD_GPU`, `RK3128_PD_MSCH`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3128-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3188-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3188-power.h

Purpose: `rk3188-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 13 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3188 (13). Representative
constants are `RK3188_PD_A9_0`, `RK3188_PD_A9_1`, `RK3188_PD_A9_2`, `RK3188_PD_A9_3`,
`RK3188_PD_DBG`, `RK3188_PD_SCU`, `RK3188_PD_VIDEO`, `RK3188_PD_VIO`, `RK3188_PD_SCU`,
`RK3188_PD_VIDEO`, `RK3188_PD_VIO`, `RK3188_PD_GPU`, `RK3188_PD_PERI`, `RK3188_PD_CPU`,
`RK3188_PD_ALIVE`, `RK3188_PD_RTC`. Function-like helpers are none. Value shape: literal numeric
range 0..12 across 13 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3188_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_LOGIC`, `VD_PMU`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 24 lines long. Notable source comments include `VD_CORE`, `VD_LOGIC`, `VD_PMU`. Example
value clusters are RK3188: `RK3188_PD_A9_0=0`, `RK3188_PD_A9_1=1`, `RK3188_PD_A9_2=2`,
`RK3188_PD_A9_3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3188_PD_A9_0`, `RK3188_PD_A9_1`, `RK3188_PD_A9_2`, `RK3188_PD_A9_3`, `RK3188_PD_DBG`,
`RK3188_PD_SCU`, `RK3188_PD_VIDEO`, `RK3188_PD_VIO`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3188-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3228-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3228-power.h

Purpose: `rk3228-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3228 (11). Representative
constants are `RK3228_PD_CORE`, `RK3228_PD_MSCH`, `RK3228_PD_BUS`, `RK3228_PD_SYS`, `RK3228_PD_VIO`,
`RK3228_PD_VOP`, `RK3228_PD_VPU`, `RK3228_PD_RKVDEC`, `RK3228_PD_SYS`, `RK3228_PD_VIO`,
`RK3228_PD_VOP`, `RK3228_PD_VPU`, `RK3228_PD_RKVDEC`, `RK3228_PD_GPU`, `RK3228_PD_PERI`,
`RK3228_PD_GMAC`. Function-like helpers are none. Value shape: literal numeric range 0..10 across 11
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3228_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RK3228 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 21 lines long. Notable source comments include `RK3228 idle id Summary.`. Example value
clusters are RK3228: `RK3228_PD_CORE=0`, `RK3228_PD_MSCH=1`, `RK3228_PD_BUS=2`, `RK3228_PD_SYS=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3228_PD_CORE`, `RK3228_PD_MSCH`, `RK3228_PD_BUS`, `RK3228_PD_SYS`, `RK3228_PD_VIO`,
`RK3228_PD_VOP`, `RK3228_PD_VPU`, `RK3228_PD_RKVDEC`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3228-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3288-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3288-power.h

Purpose: `rk3288-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 15 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3288 (15). Representative
constants are `RK3288_PD_A17_0`, `RK3288_PD_A17_1`, `RK3288_PD_A17_2`, `RK3288_PD_A17_3`,
`RK3288_PD_SCU`, `RK3288_PD_DEBUG`, `RK3288_PD_MEM`, `RK3288_PD_BUS`, `RK3288_PD_BUS`,
`RK3288_PD_PERI`, `RK3288_PD_VIO`, `RK3288_PD_ALIVE`, `RK3288_PD_HEVC`, `RK3288_PD_VIDEO`,
`RK3288_PD_GPU`, `RK3288_PD_PMU`. Function-like helpers are none. Value shape: literal numeric range
0..14 across 15 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3288_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_LOGIC`, `VD_GPU`, `VD_PMU`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 32 lines long. Notable source comments include `RK3288 Power Domain and Voltage Domain
Summary.`, `VD_CORE`, `VD_LOGIC`, `VD_GPU`, `VD_PMU`. Example value clusters are RK3288:
`RK3288_PD_A17_0=0`, `RK3288_PD_A17_1=1`, `RK3288_PD_A17_2=2`, `RK3288_PD_A17_3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3288_PD_A17_0`, `RK3288_PD_A17_1`, `RK3288_PD_A17_2`, `RK3288_PD_A17_3`, `RK3288_PD_SCU`,
`RK3288_PD_DEBUG`, `RK3288_PD_MEM`, `RK3288_PD_BUS`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3288-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3328-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3328-power.h

Purpose: `rk3328-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 10 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3328 (10). Representative
constants are `RK3328_PD_CORE`, `RK3328_PD_GPU`, `RK3328_PD_BUS`, `RK3328_PD_MSCH`,
`RK3328_PD_PERI`, `RK3328_PD_VIDEO`, `RK3328_PD_HEVC`, `RK3328_PD_SYS`, `RK3328_PD_BUS`,
`RK3328_PD_MSCH`, `RK3328_PD_PERI`, `RK3328_PD_VIDEO`, `RK3328_PD_HEVC`, `RK3328_PD_SYS`,
`RK3328_PD_VPU`, `RK3328_PD_VIO`. Function-like helpers are none. Value shape: literal numeric range
0..9 across 10 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3328_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RK3328 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include `RK3328 idle id Summary.`. Example value
clusters are RK3328: `RK3328_PD_CORE=0`, `RK3328_PD_GPU=1`, `RK3328_PD_BUS=2`, `RK3328_PD_MSCH=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3328_PD_CORE`, `RK3328_PD_GPU`, `RK3328_PD_BUS`, `RK3328_PD_MSCH`, `RK3328_PD_PERI`,
`RK3328_PD_VIDEO`, `RK3328_PD_HEVC`, `RK3328_PD_SYS`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3328-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3366-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3366-power.h

Purpose: `rk3366-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 14 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3366 (14). Representative
constants are `RK3366_PD_A53_0`, `RK3366_PD_A53_1`, `RK3366_PD_A53_2`, `RK3366_PD_A53_3`,
`RK3366_PD_BUS`, `RK3366_PD_PERI`, `RK3366_PD_VIO`, `RK3366_PD_VIDEO`, `RK3366_PD_VIO`,
`RK3366_PD_VIDEO`, `RK3366_PD_RKVDEC`, `RK3366_PD_WIFIBT`, `RK3366_PD_VPU`, `RK3366_PD_GPU`,
`RK3366_PD_ALIVE`, `RK3366_PD_PMU`. Function-like helpers are none. Value shape: literal numeric
range 0..13 across 14 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3366_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_LOGIC`, `VD_PMU`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 24 lines long. Notable source comments include `VD_CORE`, `VD_LOGIC`, `VD_PMU`. Example
value clusters are RK3366: `RK3366_PD_A53_0=0`, `RK3366_PD_A53_1=1`, `RK3366_PD_A53_2=2`,
`RK3366_PD_A53_3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3366_PD_A53_0`, `RK3366_PD_A53_1`, `RK3366_PD_A53_2`, `RK3366_PD_A53_3`, `RK3366_PD_BUS`,
`RK3366_PD_PERI`, `RK3366_PD_VIO`, `RK3366_PD_VIDEO`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3366-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3368-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3368-power.h

Purpose: `rk3368-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 18 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3368 (18). Representative
constants are `RK3368_PD_A53_L0`, `RK3368_PD_A53_L1`, `RK3368_PD_A53_L2`, `RK3368_PD_A53_L3`,
`RK3368_PD_SCU_L`, `RK3368_PD_A53_B0`, `RK3368_PD_A53_B1`, `RK3368_PD_A53_B2`, `...`,
`RK3368_PD_BUS`, `RK3368_PD_PERI`, `RK3368_PD_VIO`, `RK3368_PD_ALIVE`, `RK3368_PD_VIDEO`,
`RK3368_PD_GPU_0`, `RK3368_PD_GPU_1`, `RK3368_PD_PMU`. Function-like helpers are none. Value shape:
literal numeric range 0..17 across 18 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3368_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_LOGIC`, `VD_PMU`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 29 lines long. Notable source comments include `VD_CORE`, `VD_LOGIC`, `VD_PMU`. Example
value clusters are RK3368: `RK3368_PD_A53_L0=0`, `RK3368_PD_A53_L1=1`, `RK3368_PD_A53_L2=2`,
`RK3368_PD_A53_L3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3368_PD_A53_L0`, `RK3368_PD_A53_L1`, `RK3368_PD_A53_L2`, `RK3368_PD_A53_L3`, `RK3368_PD_SCU_L`,
`RK3368_PD_A53_B0`, `RK3368_PD_A53_B1`, `RK3368_PD_A53_B2`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3368-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3399-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3399-power.h

Purpose: `rk3399-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 37 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3399 (37). Representative
constants are `RK3399_PD_A53_L0`, `RK3399_PD_A53_L1`, `RK3399_PD_A53_L2`, `RK3399_PD_A53_L3`,
`RK3399_PD_SCU_L`, `RK3399_PD_A72_B0`, `RK3399_PD_A72_B1`, `RK3399_PD_SCU_B`, `...`,
`RK3399_PD_ALIVE`, `RK3399_PD_CENTER`, `RK3399_PD_VCODEC`, `RK3399_PD_VDU`, `RK3399_PD_RGA`,
`RK3399_PD_IEP`, `RK3399_PD_GPU`, `RK3399_PD_PMU`. Function-like helpers are none. Value shape:
literal numeric range 0..36 across 37 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3399_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE_L`, `VD_CORE_B`, `VD_LOGIC`, `VD_CENTER`, `VD_GPU`, `VD_PMU`, which is the intended
lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 54 lines long. Notable source comments include `VD_CORE_L`, `VD_CORE_B`, `VD_LOGIC`,
`VD_CENTER`, `VD_GPU`, `VD_PMU`. Example value clusters are RK3399: `RK3399_PD_A53_L0=0`,
`RK3399_PD_A53_L1=1`, `RK3399_PD_A53_L2=2`, `RK3399_PD_A53_L3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3399_PD_A53_L0`, `RK3399_PD_A53_L1`, `RK3399_PD_A53_L2`, `RK3399_PD_A53_L3`, `RK3399_PD_SCU_L`,
`RK3399_PD_A72_B0`, `RK3399_PD_A72_B1`, `RK3399_PD_SCU_B`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3399-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3568-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3568-power.h

Purpose: `rk3568-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 17 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3568 (17). Representative
constants are `RK3568_PD_CPU_0`, `RK3568_PD_CPU_1`, `RK3568_PD_CPU_2`, `RK3568_PD_CPU_3`,
`RK3568_PD_CORE_ALIVE`, `RK3568_PD_PMU`, `RK3568_PD_NPU`, `RK3568_PD_GPU`, `...`, `RK3568_PD_VO`,
`RK3568_PD_RGA`, `RK3568_PD_VPU`, `RK3568_PD_CENTER`, `RK3568_PD_RKVDEC`, `RK3568_PD_RKVENC`,
`RK3568_PD_PIPE`, `RK3568_PD_LOGIC_ALIVE`. Function-like helpers are none. Value shape: literal
numeric range 0..16 across 17 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3568_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_PMU`, `VD_NPU`, `VD_GPU`, `VD_LOGIC`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 32 lines long. Notable source comments include `VD_CORE`, `VD_PMU`, `VD_NPU`, `VD_GPU`,
`VD_LOGIC`. Example value clusters are RK3568: `RK3568_PD_CPU_0=0`, `RK3568_PD_CPU_1=1`,
`RK3568_PD_CPU_2=2`, `RK3568_PD_CPU_3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3568_PD_CPU_0`, `RK3568_PD_CPU_1`, `RK3568_PD_CPU_2`, `RK3568_PD_CPU_3`, `RK3568_PD_CORE_ALIVE`,
`RK3568_PD_PMU`, `RK3568_PD_NPU`, `RK3568_PD_GPU`. Test signals include dt_binding_check, boot-time
genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3568-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3588-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3588-power.h

Purpose: `rk3588-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 44 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3588 (44). Representative
constants are `RK3588_PD_CPU_0`, `RK3588_PD_CPU_1`, `RK3588_PD_CPU_2`, `RK3588_PD_CPU_3`,
`RK3588_PD_CPU_4`, `RK3588_PD_CPU_5`, `RK3588_PD_CPU_6`, `RK3588_PD_CPU_7`, `...`, `RK3588_PD_NVM0`,
`RK3588_PD_SDIO`, `RK3588_PD_AUDIO`, `RK3588_PD_SECURE`, `RK3588_PD_SDMMC`, `RK3588_PD_CRYPTO`,
`RK3588_PD_BUS`, `RK3588_PD_PMU1`. Function-like helpers are none. Value shape: literal numeric
range 0..43 across 44 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3588_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_LITDSU`, `VD_BIGCORE0`, `VD_BIGCORE1`, `VD_NPU`, `VD_GPU`, `VD_VCODEC`, `VD_DD01`,
`VD_DD23`, `VD_LOGIC`, `VD_PMU`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 69 lines long. Notable source comments include `VD_LITDSU`, `VD_BIGCORE0`,
`VD_BIGCORE1`, `VD_NPU`, `VD_GPU`, `VD_VCODEC`. Example value clusters are RK3588:
`RK3588_PD_CPU_0=0`, `RK3588_PD_CPU_1=1`, `RK3588_PD_CPU_2=2`, `RK3588_PD_CPU_3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3588_PD_CPU_0`, `RK3588_PD_CPU_1`, `RK3588_PD_CPU_2`, `RK3588_PD_CPU_3`, `RK3588_PD_CPU_4`,
`RK3588_PD_CPU_5`, `RK3588_PD_CPU_6`, `RK3588_PD_CPU_7`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rk3588-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3528-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3528-power.h

Purpose: `rockchip,rk3528-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3528 (9). Representative
constants are `RK3528_PD_PMU`, `RK3528_PD_BUS`, `RK3528_PD_DDR`, `RK3528_PD_MSCH`, `RK3528_PD_GPU`,
`RK3528_PD_RKVDEC`, `RK3528_PD_RKVENC`, `RK3528_PD_VO`, `RK3528_PD_BUS`, `RK3528_PD_DDR`,
`RK3528_PD_MSCH`, `RK3528_PD_GPU`, `RK3528_PD_RKVDEC`, `RK3528_PD_RKVENC`, `RK3528_PD_VO`,
`RK3528_PD_VPU`. Function-like helpers are none. Value shape: literal numeric range 0..8 across 9
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3528_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_GPU`, `VD_LOGIC`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include `VD_GPU`, `VD_LOGIC`. Example value
clusters are RK3528: `RK3528_PD_PMU=0`, `RK3528_PD_BUS=1`, `RK3528_PD_DDR=2`, `RK3528_PD_MSCH=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3528_PD_PMU`, `RK3528_PD_BUS`, `RK3528_PD_DDR`, `RK3528_PD_MSCH`, `RK3528_PD_GPU`,
`RK3528_PD_RKVDEC`, `RK3528_PD_RKVENC`, `RK3528_PD_VO`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3528-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3562-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3562-power.h

Purpose: `rockchip,rk3562-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 17 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3562 (17). Representative
constants are `RK3562_PD_CPU_0`, `RK3562_PD_CPU_1`, `RK3562_PD_CPU_2`, `RK3562_PD_CPU_3`,
`RK3562_PD_CORE_ALIVE`, `RK3562_PD_PMU`, `RK3562_PD_PMU_ALIVE`, `RK3562_PD_NPU`, `...`,
`RK3562_PD_DDR`, `RK3562_PD_VEPU`, `RK3562_PD_VDPU`, `RK3562_PD_VI`, `RK3562_PD_VO`,
`RK3562_PD_RGA`, `RK3562_PD_PHP`, `RK3562_PD_LOGIC_ALIVE`. Function-like helpers are none. Value
shape: literal numeric range 0..16 across 17 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3562_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_PMU`, `VD_NPU`, `VD_GPU`, `VD_LOGIC`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 35 lines long. Notable source comments include `VD_CORE`, `VD_PMU`, `VD_NPU`, `VD_GPU`,
`VD_LOGIC`. Example value clusters are RK3562: `RK3562_PD_CPU_0=0`, `RK3562_PD_CPU_1=1`,
`RK3562_PD_CPU_2=2`, `RK3562_PD_CPU_3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3562_PD_CPU_0`, `RK3562_PD_CPU_1`, `RK3562_PD_CPU_2`, `RK3562_PD_CPU_3`, `RK3562_PD_CORE_ALIVE`,
`RK3562_PD_PMU`, `RK3562_PD_PMU_ALIVE`, `RK3562_PD_NPU`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3562-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3576-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3576-power.h

Purpose: `rockchip,rk3576-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 19 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RK3576 (19). Representative
constants are `RK3576_PD_NPU`, `RK3576_PD_NPUTOP`, `RK3576_PD_NPU0`, `RK3576_PD_NPU1`,
`RK3576_PD_GPU`, `RK3576_PD_NVM`, `RK3576_PD_SDGMAC`, `RK3576_PD_USB`, `...`, `RK3576_PD_VEPU0`,
`RK3576_PD_VEPU1`, `RK3576_PD_VPU`, `RK3576_PD_VDEC`, `RK3576_PD_VI`, `RK3576_PD_VO0`,
`RK3576_PD_VO1`, `RK3576_PD_VOP`. Function-like helpers are none. Value shape: literal numeric range
0..18 across 19 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RK3576_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_NPU`, `VD_GPU`, `VD_LOGIC`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 30 lines long. Notable source comments include `VD_NPU`, `VD_GPU`, `VD_LOGIC`. Example
value clusters are RK3576: `RK3576_PD_NPU=0`, `RK3576_PD_NPUTOP=1`, `RK3576_PD_NPU0=2`,
`RK3576_PD_NPU1=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RK3576_PD_NPU`, `RK3576_PD_NPUTOP`, `RK3576_PD_NPU0`, `RK3576_PD_NPU1`, `RK3576_PD_GPU`,
`RK3576_PD_NVM`, `RK3576_PD_SDGMAC`, `RK3576_PD_USB`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rk3576-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rv1126-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rv1126-power.h

Purpose: `rockchip,rv1126-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 19 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RV1126 (19). Representative
constants are `RV1126_PD_CPU_0`, `RV1126_PD_CPU_1`, `RV1126_PD_CPU_2`, `RV1126_PD_CPU_3`,
`RV1126_PD_CORE_ALIVE`, `RV1126_PD_PMU`, `RV1126_PD_PMU_ALIVE`, `RV1126_PD_NPU`, `...`,
`RV1126_PD_ISPP`, `RV1126_PD_VDPU`, `RV1126_PD_CRYPTO`, `RV1126_PD_DDR`, `RV1126_PD_NVM`,
`RV1126_PD_SDIO`, `RV1126_PD_USB`, `RV1126_PD_LOGIC_ALIVE`. Function-like helpers are none. Value
shape: literal numeric range 0..18 across 19 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RV1126_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `VD_CORE`, `VD_PMU`, `VD_NPU`, `VD_VEPU`, `VD_LOGIC`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 35 lines long. Notable source comments include `VD_CORE`, `VD_PMU`, `VD_NPU`, `VD_VEPU`,
`VD_LOGIC`. Example value clusters are RV1126: `RV1126_PD_CPU_0=0`, `RV1126_PD_CPU_1=1`,
`RV1126_PD_CPU_2=2`, `RV1126_PD_CPU_3=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RV1126_PD_CPU_0`, `RV1126_PD_CPU_1`, `RV1126_PD_CPU_2`, `RV1126_PD_CPU_3`, `RV1126_PD_CORE_ALIVE`,
`RV1126_PD_PMU`, `RV1126_PD_PMU_ALIVE`, `RV1126_PD_NPU`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rv1126-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rv1126b-power-controller.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rv1126b-power-controller.h

Purpose: `rockchip,rv1126b-power-controller.h` is a Devicetree binding header for a power-domain provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are RV1126B (3). Representative
constants are `RV1126B_PD_NPU`, `RV1126B_PD_VDO`, `RV1126B_PD_AIISP`, `RV1126B_PD_NPU`,
`RV1126B_PD_VDO`, `RV1126B_PD_AIISP`. Function-like helpers are none. Value shape: literal numeric
range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_RV1126B_POWER_CONTROLLER_H__`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `VD_NPU`, `VD_LOGIC`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 17 lines long. Notable source comments include `VD_NPU`, `VD_LOGIC`. Example value
clusters are RV1126B: `RV1126B_PD_NPU=0`, `RV1126B_PD_VDO=1`, `RV1126B_PD_AIISP=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`RV1126B_PD_NPU`, `RV1126B_PD_VDO`, `RV1126B_PD_AIISP`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/rockchip,rv1126b-power-controller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/starfive,jh7110-pmu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/starfive,jh7110-pmu.h

Purpose: `starfive,jh7110-pmu.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are JH7110 (9). Representative
constants are `JH7110_PD_SYSTOP`, `JH7110_PD_CPU`, `JH7110_PD_GPUA`, `JH7110_PD_VDEC`,
`JH7110_PD_VOUT`, `JH7110_PD_ISP`, `JH7110_PD_VENC`, `JH7110_AON_PD_DPHY_TX`, `JH7110_PD_CPU`,
`JH7110_PD_GPUA`, `JH7110_PD_VDEC`, `JH7110_PD_VOUT`, `JH7110_PD_ISP`, `JH7110_PD_VENC`,
`JH7110_AON_PD_DPHY_TX`, `JH7110_AON_PD_DPHY_RX`. Function-like helpers are none. Value shape:
literal numeric range 0..6 across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_JH7110_POWER_H__`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `AON Power Domain`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 21 lines long. Notable source comments include `AON Power Domain`. Example value
clusters are JH7110: `JH7110_PD_SYSTOP=0`, `JH7110_PD_CPU=1`, `JH7110_PD_GPUA=2`,
`JH7110_PD_VDEC=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`JH7110_PD_SYSTOP`, `JH7110_PD_CPU`, `JH7110_PD_GPUA`, `JH7110_PD_VDEC`, `JH7110_PD_VOUT`,
`JH7110_PD_ISP`, `JH7110_PD_VENC`, `JH7110_AON_PD_DPHY_TX`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/starfive,jh7110-pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/summit,smb347-charger.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/summit,smb347-charger.h

Purpose: `summit,smb347-charger.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are SMB3XX (8). Representative
constants are `SMB3XX_SOFT_TEMP_COMPENSATE_NONE`, `SMB3XX_SOFT_TEMP_COMPENSATE_CURRENT`,
`SMB3XX_SOFT_TEMP_COMPENSATE_VOLTAGE`, `SMB3XX_CHG_ENABLE_SW`, `SMB3XX_CHG_ENABLE_PIN_ACTIVE_LOW`,
`SMB3XX_CHG_ENABLE_PIN_ACTIVE_HIGH`, `SMB3XX_SYSOK_INOK_ACTIVE_LOW`,
`SMB3XX_SYSOK_INOK_ACTIVE_HIGH`, `SMB3XX_SOFT_TEMP_COMPENSATE_NONE`,
`SMB3XX_SOFT_TEMP_COMPENSATE_CURRENT`, `SMB3XX_SOFT_TEMP_COMPENSATE_VOLTAGE`,
`SMB3XX_CHG_ENABLE_SW`, `SMB3XX_CHG_ENABLE_PIN_ACTIVE_LOW`, `SMB3XX_CHG_ENABLE_PIN_ACTIVE_HIGH`,
`SMB3XX_SYSOK_INOK_ACTIVE_LOW`, `SMB3XX_SYSOK_INOK_ACTIVE_HIGH`. Function-like helpers are none.
Value shape: literal numeric range 0..2 across 8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_SMB347_CHARGER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`Charging compensation method`, `Charging enable control`, `Polarity of INOK signal`, which is the
intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 23 lines long. Notable source comments include `Charging compensation method`, `Charging
enable control`, `Polarity of INOK signal`. Example value clusters are SMB3XX:
`SMB3XX_SOFT_TEMP_COMPENSATE_NONE=0`, `SMB3XX_SOFT_TEMP_COMPENSATE_CURRENT=1`,
`SMB3XX_SOFT_TEMP_COMPENSATE_VOLTAGE=2`, `SMB3XX_CHG_ENABLE_SW=0`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`SMB3XX_SOFT_TEMP_COMPENSATE_NONE`, `SMB3XX_SOFT_TEMP_COMPENSATE_CURRENT`,
`SMB3XX_SOFT_TEMP_COMPENSATE_VOLTAGE`, `SMB3XX_CHG_ENABLE_SW`, `SMB3XX_CHG_ENABLE_PIN_ACTIVE_LOW`,
`SMB3XX_CHG_ENABLE_PIN_ACTIVE_HIGH`, `SMB3XX_SYSOK_INOK_ACTIVE_LOW`,
`SMB3XX_SYSOK_INOK_ACTIVE_HIGH`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/summit,smb347-charger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra186-powergate.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra186-powergate.h

Purpose: `tegra186-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 18 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are TEGRA186 (18). Representative
constants are `TEGRA186_POWER_DOMAIN_AUD`, `TEGRA186_POWER_DOMAIN_DFD`,
`TEGRA186_POWER_DOMAIN_DISP`, `TEGRA186_POWER_DOMAIN_DISPB`, `TEGRA186_POWER_DOMAIN_DISPC`,
`TEGRA186_POWER_DOMAIN_ISPA`, `TEGRA186_POWER_DOMAIN_NVDEC`, `TEGRA186_POWER_DOMAIN_NVJPG`, `...`,
`TEGRA186_POWER_DOMAIN_SAX`, `TEGRA186_POWER_DOMAIN_VE`, `TEGRA186_POWER_DOMAIN_VIC`,
`TEGRA186_POWER_DOMAIN_XUSBA`, `TEGRA186_POWER_DOMAIN_XUSBB`, `TEGRA186_POWER_DOMAIN_XUSBC`,
`TEGRA186_POWER_DOMAIN_GPU`, `TEGRA186_POWER_DOMAIN_MAX`. Function-like helpers are none. Value
shape: literal numeric range 0..44 across 18 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_TEGRA186_POWERGATE_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `TEGRA186 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 28 lines long. Notable source comments include none. Example value clusters are
TEGRA186: `TEGRA186_POWER_DOMAIN_AUD=0`, `TEGRA186_POWER_DOMAIN_DFD=1`,
`TEGRA186_POWER_DOMAIN_DISP=2`, `TEGRA186_POWER_DOMAIN_DISPB=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`TEGRA186_POWER_DOMAIN_AUD`, `TEGRA186_POWER_DOMAIN_DFD`, `TEGRA186_POWER_DOMAIN_DISP`,
`TEGRA186_POWER_DOMAIN_DISPB`, `TEGRA186_POWER_DOMAIN_DISPC`, `TEGRA186_POWER_DOMAIN_ISPA`,
`TEGRA186_POWER_DOMAIN_NVDEC`, `TEGRA186_POWER_DOMAIN_NVJPG`. Test signals include dt_binding_check,
boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM
smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra186-powergate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra194-powergate.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra194-powergate.h

Purpose: `tegra194-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 27 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are TEGRA194 (27). Representative
constants are `TEGRA194_POWER_DOMAIN_AUD`, `TEGRA194_POWER_DOMAIN_DISP`,
`TEGRA194_POWER_DOMAIN_DISPB`, `TEGRA194_POWER_DOMAIN_DISPC`, `TEGRA194_POWER_DOMAIN_ISPA`,
`TEGRA194_POWER_DOMAIN_NVDECA`, `TEGRA194_POWER_DOMAIN_NVJPG`, `TEGRA194_POWER_DOMAIN_NVENCA`,
`...`, `TEGRA194_POWER_DOMAIN_PCIEX8B`, `TEGRA194_POWER_DOMAIN_PVAA`, `TEGRA194_POWER_DOMAIN_PVAB`,
`TEGRA194_POWER_DOMAIN_DLAA`, `TEGRA194_POWER_DOMAIN_DLAB`, `TEGRA194_POWER_DOMAIN_CV`,
`TEGRA194_POWER_DOMAIN_GPU`, `TEGRA194_POWER_DOMAIN_MAX`. Function-like helpers are none. Value
shape: literal numeric range 1..27 across 27 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__ABI_MACH_T194_POWERGATE_T194_H_`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`TEGRA194 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 35 lines long. Notable source comments include none. Example value clusters are
TEGRA194: `TEGRA194_POWER_DOMAIN_AUD=1`, `TEGRA194_POWER_DOMAIN_DISP=2`,
`TEGRA194_POWER_DOMAIN_DISPB=3`, `TEGRA194_POWER_DOMAIN_DISPC=4`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`TEGRA194_POWER_DOMAIN_AUD`, `TEGRA194_POWER_DOMAIN_DISP`, `TEGRA194_POWER_DOMAIN_DISPB`,
`TEGRA194_POWER_DOMAIN_DISPC`, `TEGRA194_POWER_DOMAIN_ISPA`, `TEGRA194_POWER_DOMAIN_NVDECA`,
`TEGRA194_POWER_DOMAIN_NVJPG`, `TEGRA194_POWER_DOMAIN_NVENCA`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra194-powergate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra234-powergate.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra234-powergate.h

Purpose: `tegra234-powergate.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 31 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are TEGRA234 (31). Representative
constants are `TEGRA234_POWER_DOMAIN_OFA`, `TEGRA234_POWER_DOMAIN_AUD`,
`TEGRA234_POWER_DOMAIN_DISP`, `TEGRA234_POWER_DOMAIN_PCIEX8A`, `TEGRA234_POWER_DOMAIN_PCIEX4A`,
`TEGRA234_POWER_DOMAIN_PCIEX4BA`, `TEGRA234_POWER_DOMAIN_PCIEX4BB`, `TEGRA234_POWER_DOMAIN_PCIEX1A`,
`...`, `TEGRA234_POWER_DOMAIN_VI`, `TEGRA234_POWER_DOMAIN_VIC`, `TEGRA234_POWER_DOMAIN_PVA`,
`TEGRA234_POWER_DOMAIN_DLAA`, `TEGRA234_POWER_DOMAIN_DLAB`, `TEGRA234_POWER_DOMAIN_CV`,
`TEGRA234_POWER_DOMAIN_GPU`, `TEGRA234_POWER_DOMAIN_NVJPGB`. Function-like helpers are none. Value
shape: 31 alias or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__ABI_MACH_T234_POWERGATE_T234_H_`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`TEGRA234 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 39 lines long. Notable source comments include none. Example value clusters are
TEGRA234: `TEGRA234_POWER_DOMAIN_OFA=1U`, `TEGRA234_POWER_DOMAIN_AUD=2U`,
`TEGRA234_POWER_DOMAIN_DISP=3U`, `TEGRA234_POWER_DOMAIN_PCIEX8A=5U`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`TEGRA234_POWER_DOMAIN_OFA`, `TEGRA234_POWER_DOMAIN_AUD`, `TEGRA234_POWER_DOMAIN_DISP`,
`TEGRA234_POWER_DOMAIN_PCIEX8A`, `TEGRA234_POWER_DOMAIN_PCIEX4A`, `TEGRA234_POWER_DOMAIN_PCIEX4BA`,
`TEGRA234_POWER_DOMAIN_PCIEX4BB`, `TEGRA234_POWER_DOMAIN_PCIEX1A`. Test signals include
dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing, suspend/resume, and
device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/tegra234-powergate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/thead,th1520-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/thead,th1520-power.h

Purpose: `thead,th1520-power.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are TH1520 (7). Representative
constants are `TH1520_AUDIO_PD`, `TH1520_VDEC_PD`, `TH1520_NPU_PD`, `TH1520_VENC_PD`,
`TH1520_GPU_PD`, `TH1520_DSP0_PD`, `TH1520_DSP1_PD`, `TH1520_AUDIO_PD`, `TH1520_VDEC_PD`,
`TH1520_NPU_PD`, `TH1520_VENC_PD`, `TH1520_GPU_PD`, `TH1520_DSP0_PD`, `TH1520_DSP1_PD`. Function-
like helpers are none. Value shape: literal numeric range 0..6 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_POWER_TH1520_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`TH1520 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 19 lines long. Notable source comments include none. Example value clusters are TH1520:
`TH1520_AUDIO_PD=0`, `TH1520_VDEC_PD=1`, `TH1520_NPU_PD=2`, `TH1520_VENC_PD=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`TH1520_AUDIO_PD`, `TH1520_VDEC_PD`, `TH1520_NPU_PD`, `TH1520_VENC_PD`, `TH1520_GPU_PD`,
`TH1520_DSP0_PD`, `TH1520_DSP1_PD`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/thead,th1520-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/xlnx-zynqmp-power.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/power/xlnx-zynqmp-power.h

Purpose: `xlnx-zynqmp-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 35 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_R5 (4), PD_TTC (4), PD_ETH (4),
PD_RPU (2), PD_USB (2), PD_UART (2), PD_SPI (2), PD_I2C (2), PD_SD (2), PD_CAN (2). Representative
constants are `PD_RPU_0`, `PD_RPU_1`, `PD_R5_0_ATCM`, `PD_R5_0_BTCM`, `PD_R5_1_ATCM`,
`PD_R5_1_BTCM`, `PD_USB_0`, `PD_USB_1`, `...`, `PD_ADMA`, `PD_NAND`, `PD_QSPI`, `PD_GPIO`,
`PD_CAN_0`, `PD_CAN_1`, `PD_GPU`, `PD_PCIE`. Function-like helpers are none. Value shape: literal
numeric range 7..59 across 35 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_ZYNQMP_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PD_R5 group`, `PD_TTC group`, `PD_ETH group`, `PD_RPU group`, `PD_USB group`, `PD_UART group`,
`PD_SPI group`, `PD_I2C group`, `PD_SD group`, `PD_CAN group`, `PD_SATA group`, `PD_DP group`, which
is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 45 lines long. Notable source comments include none. Example value clusters are PD_R5:
`PD_R5_0_ATCM=15`, `PD_R5_0_BTCM=16`, `PD_R5_1_ATCM=17`, `PD_R5_1_BTCM=18`; PD_TTC: `PD_TTC_0=24`,
`PD_TTC_1=25`, `PD_TTC_2=26`, `PD_TTC_3=27`; PD_ETH: `PD_ETH_0=29`, `PD_ETH_1=30`, `PD_ETH_2=31`,
`PD_ETH_3=32`; PD_RPU: `PD_RPU_0=7`, `PD_RPU_1=8`; PD_USB: `PD_USB_0=22`, `PD_USB_1=23`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_RPU_0`, `PD_RPU_1`, `PD_R5_0_ATCM`, `PD_R5_0_BTCM`, `PD_R5_1_ATCM`, `PD_R5_1_BTCM`, `PD_USB_0`,
`PD_USB_1`. Test signals include dt_binding_check, boot-time genpd attachment, power-domain on/off
sequencing, suspend/resume, and device runtime-PM smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/power/xlnx-zynqmp-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pwm/pwm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pwm/pwm.h

Purpose: `pwm.h` is a Devicetree binding header for a PWM provider. It exports numeric C preprocessor
constants that DTS files and provider drivers share as the ABI for phandle cells, selector values,
and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 1 `#define`s covering PWM polarity, channel, or
firmware control constants. The main macro families are PWM_POLARITY (1). Representative constants
are `PWM_POLARITY_INVERTED`, `PWM_POLARITY_INVERTED`. Function-like helpers are none. Value shape: 1
expression values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PWM_PWM_H`; after preprocessing, DTS C-preprocessor users and C drivers see only the
constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWM_POLARITY group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are PWM providers, fan/backlight nodes, and
firmware PWM consumers.

Local source signals: The file is 15 lines long. Notable source comments include `This header provides constants for most
PWM bindings. Most PWM bindings can include a flags cell as part of the PWM specifier. In most
cases, the format of the flags cell uses the standard values defined in this header.`. Example value
clusters are PWM_POLARITY: `PWM_POLARITY_INVERTED=(1 << 0)`.

Risks and test signals: Primary risks are polarity or channel constant drift can invert outputs or address the wrong
firmware PWM endpoint. Pay special attention to exported symbols such as `PWM_POLARITY_INVERTED`.
Test signals include DTS compile checks, PWM sysfs/debugfs inspection, fan/backlight behavior, and
polarity regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pwm/pwm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pwm/raspberrypi,firmware-poe-pwm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pwm/raspberrypi,firmware-poe-pwm.h

Purpose: `raspberrypi,firmware-poe-pwm.h` is a Devicetree binding header for a PWM provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering PWM polarity, channel, or
firmware control constants. The main macro families are RASPBERRYPI (2). Representative constants
are `RASPBERRYPI_FIRMWARE_PWM_POE`, `RASPBERRYPI_FIRMWARE_PWM_NUM`, `RASPBERRYPI_FIRMWARE_PWM_POE`,
`RASPBERRYPI_FIRMWARE_PWM_NUM`. Function-like helpers are none. Value shape: literal numeric range
0..1 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RASPBERRYPI_FIRMWARE_PWM_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RASPBERRYPI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are PWM providers, fan/backlight nodes, and
firmware PWM consumers.

Local source signals: The file is 13 lines long. Notable source comments include none. Example value clusters are
RASPBERRYPI: `RASPBERRYPI_FIRMWARE_PWM_POE=0`, `RASPBERRYPI_FIRMWARE_PWM_NUM=1`.

Risks and test signals: Primary risks are polarity or channel constant drift can invert outputs or address the wrong
firmware PWM endpoint. Pay special attention to exported symbols such as
`RASPBERRYPI_FIRMWARE_PWM_POE`, `RASPBERRYPI_FIRMWARE_PWM_NUM`. Test signals include DTS compile
checks, PWM sysfs/debugfs inspection, fan/backlight behavior, and polarity regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pwm/raspberrypi,firmware-poe-pwm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/active-semi,8865-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/active-semi,8865-regulator.h

Purpose: `active-semi,8865-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are ACT8865 (3). Representative constants are
`ACT8865_REGULATOR_MODE_FIXED`, `ACT8865_REGULATOR_MODE_NORMAL`, `ACT8865_REGULATOR_MODE_LOWPOWER`,
`ACT8865_REGULATOR_MODE_FIXED`, `ACT8865_REGULATOR_MODE_NORMAL`, `ACT8865_REGULATOR_MODE_LOWPOWER`.
Function-like helpers are none. Value shape: literal numeric range 1..3 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_ACT8865_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`ACT8865 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 28 lines long. Notable source comments include `Device Tree binding constants for the
ACT8865 PMIC regulators`, `These constants should be used to specify regulator modes in device tree
for ACT8865 regulators as follows: ACT8865_REGULATOR_MODE_FIXED: It is specific to DCDC regulators
and it specifies the usage of fixed-frequency PWM. ACT8865_REGULATOR_MODE_NORMAL: It is specific to
LDO regulators and it specifies the usage of normal mode. ACT8865_REGULATOR_MODE_LOWPOWER: For DCDC
and LDO regulators; it specify the usage of proprietary power-saving mode.`. Example value clusters
are ACT8865: `ACT8865_REGULATOR_MODE_FIXED=1`, `ACT8865_REGULATOR_MODE_NORMAL=2`,
`ACT8865_REGULATOR_MODE_LOWPOWER=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `ACT8865_REGULATOR_MODE_FIXED`,
`ACT8865_REGULATOR_MODE_NORMAL`, `ACT8865_REGULATOR_MODE_LOWPOWER`. Test signals include regulator
schema validation, PMIC probe, regulator summary inspection, voltage/mode transition checks, and
suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/active-semi,8865-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/active-semi,8945a-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/active-semi,8945a-regulator.h

Purpose: `active-semi,8945a-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are ACT8945A (3). Representative constants are
`ACT8945A_REGULATOR_MODE_FIXED`, `ACT8945A_REGULATOR_MODE_NORMAL`,
`ACT8945A_REGULATOR_MODE_LOWPOWER`, `ACT8945A_REGULATOR_MODE_FIXED`,
`ACT8945A_REGULATOR_MODE_NORMAL`, `ACT8945A_REGULATOR_MODE_LOWPOWER`. Function-like helpers are
none. Value shape: literal numeric range 1..3 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_ACT8945A_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`ACT8945A group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 30 lines long. Notable source comments include `Device Tree binding constants for the
ACT8945A PMIC regulators`, `These constants should be used to specify regulator modes in device tree
for ACT8945A regulators as follows: ACT8945A_REGULATOR_MODE_FIXED: It is specific to DCDC regulators
and it specifies the usage of fixed-frequency PWM. ACT8945A_REGULATOR_MODE_NORMAL: It is specific to
LDO regulators and it specifies the usage of normal mode. ACT8945A_REGULATOR_MODE_LOWPOWER: For DCDC
and LDO regulators; it specify the usage of proprietary power-saving mode.`. Example value clusters
are ACT8945A: `ACT8945A_REGULATOR_MODE_FIXED=1`, `ACT8945A_REGULATOR_MODE_NORMAL=2`,
`ACT8945A_REGULATOR_MODE_LOWPOWER=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `ACT8945A_REGULATOR_MODE_FIXED`,
`ACT8945A_REGULATOR_MODE_NORMAL`, `ACT8945A_REGULATOR_MODE_LOWPOWER`. Test signals include regulator
schema validation, PMIC probe, regulator summary inspection, voltage/mode transition checks, and
suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/active-semi,8945a-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/dlg,da9063-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/dlg,da9063-regulator.h

Purpose: `dlg,da9063-regulator.h` is a Devicetree binding header for a regulator provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are DA9063 (3). Representative constants are
`DA9063_BUCK_MODE_SLEEP`, `DA9063_BUCK_MODE_SYNC`, `DA9063_BUCK_MODE_AUTO`,
`DA9063_BUCK_MODE_SLEEP`, `DA9063_BUCK_MODE_SYNC`, `DA9063_BUCK_MODE_AUTO`. Function-like helpers
are none. Value shape: literal numeric range 1..3 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_DLG_DA9063_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `DA9063 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 16 lines long. Notable source comments include `These buck mode constants may be used to
specify values in device tree properties (e.g. regulator-initial-mode). A description of the
following modes is in the manufacturers datasheet.`. Example value clusters are DA9063:
`DA9063_BUCK_MODE_SLEEP=1`, `DA9063_BUCK_MODE_SYNC=2`, `DA9063_BUCK_MODE_AUTO=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `DA9063_BUCK_MODE_SLEEP`,
`DA9063_BUCK_MODE_SYNC`, `DA9063_BUCK_MODE_AUTO`. Test signals include regulator schema validation,
PMIC probe, regulator summary inspection, voltage/mode transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/dlg,da9063-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/dlg,da9121-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/dlg,da9121-regulator.h

Purpose: `dlg,da9121-regulator.h` is a Devicetree binding header for a regulator provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are DA9121 (8). Representative constants are
`DA9121_BUCK_MODE_FORCE_PFM`, `DA9121_BUCK_MODE_FORCE_PWM`, `DA9121_BUCK_MODE_FORCE_PWM_SHEDDING`,
`DA9121_BUCK_MODE_AUTO`, `DA9121_BUCK_RIPPLE_CANCEL_NONE`, `DA9121_BUCK_RIPPLE_CANCEL_SMALL`,
`DA9121_BUCK_RIPPLE_CANCEL_MID`, `DA9121_BUCK_RIPPLE_CANCEL_LARGE`, `DA9121_BUCK_MODE_FORCE_PFM`,
`DA9121_BUCK_MODE_FORCE_PWM`, `DA9121_BUCK_MODE_FORCE_PWM_SHEDDING`, `DA9121_BUCK_MODE_AUTO`,
`DA9121_BUCK_RIPPLE_CANCEL_NONE`, `DA9121_BUCK_RIPPLE_CANCEL_SMALL`,
`DA9121_BUCK_RIPPLE_CANCEL_MID`, `DA9121_BUCK_RIPPLE_CANCEL_LARGE`. Function-like helpers are none.
Value shape: literal numeric range 0..3 across 8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_DLG_DA9121_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `DA9121 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 22 lines long. Notable source comments include `These buck mode constants may be used to
specify values in device tree properties (e.g. regulator-initial-mode). A description of the
following modes is in the manufacturers datasheet.`. Example value clusters are DA9121:
`DA9121_BUCK_MODE_FORCE_PFM=0`, `DA9121_BUCK_MODE_FORCE_PWM=1`,
`DA9121_BUCK_MODE_FORCE_PWM_SHEDDING=2`, `DA9121_BUCK_MODE_AUTO=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `DA9121_BUCK_MODE_FORCE_PFM`,
`DA9121_BUCK_MODE_FORCE_PWM`, `DA9121_BUCK_MODE_FORCE_PWM_SHEDDING`, `DA9121_BUCK_MODE_AUTO`,
`DA9121_BUCK_RIPPLE_CANCEL_NONE`, `DA9121_BUCK_RIPPLE_CANCEL_SMALL`,
`DA9121_BUCK_RIPPLE_CANCEL_MID`, `DA9121_BUCK_RIPPLE_CANCEL_LARGE`. Test signals include regulator
schema validation, PMIC probe, regulator summary inspection, voltage/mode transition checks, and
suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/dlg,da9121-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/dlg,da9211-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/dlg,da9211-regulator.h

Purpose: `dlg,da9211-regulator.h` is a Devicetree binding header for a regulator provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are DA9211 (3). Representative constants are
`DA9211_BUCK_MODE_SLEEP`, `DA9211_BUCK_MODE_SYNC`, `DA9211_BUCK_MODE_AUTO`,
`DA9211_BUCK_MODE_SLEEP`, `DA9211_BUCK_MODE_SYNC`, `DA9211_BUCK_MODE_AUTO`. Function-like helpers
are none. Value shape: literal numeric range 1..3 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_DLG_DA9211_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `DA9211 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 16 lines long. Notable source comments include `These buck mode constants may be used to
specify values in device tree properties (e.g. regulator-initial-mode, regulator-allowed-modes). A
description of the following modes is in the manufacturers datasheet.`. Example value clusters are
DA9211: `DA9211_BUCK_MODE_SLEEP=1`, `DA9211_BUCK_MODE_SYNC=2`, `DA9211_BUCK_MODE_AUTO=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `DA9211_BUCK_MODE_SLEEP`,
`DA9211_BUCK_MODE_SYNC`, `DA9211_BUCK_MODE_AUTO`. Test signals include regulator schema validation,
PMIC probe, regulator summary inspection, voltage/mode transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/dlg,da9211-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/maxim,max77802.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/maxim,max77802.h

Purpose: `maxim,max77802.h` is a Devicetree binding header for a regulator provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are MAX77802 (2). Representative constants are
`MAX77802_OPMODE_LP`, `MAX77802_OPMODE_NORMAL`, `MAX77802_OPMODE_LP`, `MAX77802_OPMODE_NORMAL`.
Function-like helpers are none. Value shape: literal numeric range 1..3 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_MAXIM_MAX77802_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `Regulator operating modes`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 15 lines long. Notable source comments include `Device Tree binding constants for the
Maxim 77802 PMIC regulators`, `Regulator operating modes`,
`_DT_BINDINGS_REGULATOR_MAXIM_MAX77802_H`. Example value clusters are MAX77802:
`MAX77802_OPMODE_LP=1`, `MAX77802_OPMODE_NORMAL=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `MAX77802_OPMODE_LP`,
`MAX77802_OPMODE_NORMAL`. Test signals include regulator schema validation, PMIC probe, regulator
summary inspection, voltage/mode transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/maxim,max77802.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/mediatek,mt6360-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/mediatek,mt6360-regulator.h

Purpose: `mediatek,mt6360-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are MT6360 (3). Representative constants are
`MT6360_OPMODE_LP`, `MT6360_OPMODE_ULP`, `MT6360_OPMODE_NORMAL`, `MT6360_OPMODE_LP`,
`MT6360_OPMODE_ULP`, `MT6360_OPMODE_NORMAL`. Function-like helpers are none. Value shape: literal
numeric range 0..3 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_MEDIATEK_MT6360_REGULATOR_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `MT6360 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 16 lines long. Notable source comments include `BUCK/LDO mode constants which may be
used in devicetree properties (eg. regulator-allowed-modes). See the manufacturer's datasheet for
more information on these modes.`. Example value clusters are MT6360: `MT6360_OPMODE_LP=2`,
`MT6360_OPMODE_ULP=3`, `MT6360_OPMODE_NORMAL=0`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `MT6360_OPMODE_LP`,
`MT6360_OPMODE_ULP`, `MT6360_OPMODE_NORMAL`. Test signals include regulator schema validation, PMIC
probe, regulator summary inspection, voltage/mode transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/mediatek,mt6360-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/mediatek,mt6397-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/mediatek,mt6397-regulator.h

Purpose: `mediatek,mt6397-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are MT6397 (2). Representative constants are
`MT6397_BUCK_MODE_AUTO`, `MT6397_BUCK_MODE_FORCE_PWM`, `MT6397_BUCK_MODE_AUTO`,
`MT6397_BUCK_MODE_FORCE_PWM`. Function-like helpers are none. Value shape: literal numeric range
0..1 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_MEDIATEK_MT6397_H_`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `MT6397 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 15 lines long. Notable source comments include `Buck mode constants which may be used in
devicetree properties (eg. regulator-initial-mode, regulator-allowed-modes). See the manufacturer's
datasheet for more information on these modes.`. Example value clusters are MT6397:
`MT6397_BUCK_MODE_AUTO=0`, `MT6397_BUCK_MODE_FORCE_PWM=1`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `MT6397_BUCK_MODE_AUTO`,
`MT6397_BUCK_MODE_FORCE_PWM`. Test signals include regulator schema validation, PMIC probe,
regulator summary inspection, voltage/mode transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/mediatek,mt6397-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/nxp,pca9450-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/nxp,pca9450-regulator.h

Purpose: `nxp,pca9450-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are PCA9450 (2). Representative constants are
`PCA9450_BUCK_MODE_AUTO`, `PCA9450_BUCK_MODE_FORCE_PWM`, `PCA9450_BUCK_MODE_AUTO`,
`PCA9450_BUCK_MODE_FORCE_PWM`. Function-like helpers are none. Value shape: literal numeric range
0..1 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATORS_NXP_PCA9450_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PCA9450 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 18 lines long. Notable source comments include `Device Tree binding constants for the
NXP PCA9450A/B/C PMIC regulators`, `Buck mode constants which may be used in devicetree properties
(eg. regulator-initial-mode, regulator-allowed-modes). See the manufacturer's datasheet for more
information on these modes.`. Example value clusters are PCA9450: `PCA9450_BUCK_MODE_AUTO=0`,
`PCA9450_BUCK_MODE_FORCE_PWM=1`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `PCA9450_BUCK_MODE_AUTO`,
`PCA9450_BUCK_MODE_FORCE_PWM`. Test signals include regulator schema validation, PMIC probe,
regulator summary inspection, voltage/mode transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/nxp,pca9450-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/qcom,rpmh-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/qcom,rpmh-regulator.h

Purpose: `qcom,rpmh-regulator.h` is a Devicetree binding header for a regulator provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 4 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are RPMH (4). Representative constants are
`RPMH_REGULATOR_MODE_RET`, `RPMH_REGULATOR_MODE_LPM`, `RPMH_REGULATOR_MODE_AUTO`,
`RPMH_REGULATOR_MODE_HPM`, `RPMH_REGULATOR_MODE_RET`, `RPMH_REGULATOR_MODE_LPM`,
`RPMH_REGULATOR_MODE_AUTO`, `RPMH_REGULATOR_MODE_HPM`. Function-like helpers are none. Value shape:
literal numeric range 0..3 across 4 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__QCOM_RPMH_REGULATOR_H`; after preprocessing, DTS C-preprocessor users and C drivers see only the
constants and any packing helpers. Comment-delimited groups or observed macro clusters are `RPMH
group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 36 lines long. Notable source comments include `These mode constants may be used to
specify modes for various RPMh regulator device tree properties (e.g. regulator-initial-mode). Each
type of regulator supports a subset of the possible modes. %RPMH_REGULATOR_MODE_RET: Retention mode
in which only an extremely small load current is allowed. This mode is supported by LDO and SMPS
type regulators. %RPMH_REGULATOR_MODE_LPM: Low power mode in which a small load current is allowed.
This mode corresponds to PFM for SMPS and BOB type regulators. This mode is supported by LDO,
HFSMPS, BOB, and PMIC4 FTSMPS type regulators. %RPMH_REGULATOR_MODE_AUTO: Auto mode in which the
regulator hardware automatically switches between LPM and HPM based upon the real-time load current.
This mode is supported by HFSMPS, BOB, and PMIC4 FTSMPS type regulators. %RPMH_REGULATOR_MODE_HPM:
High power mode in which the full rated current of the regulator is allowed. This mode corresponds
to PWM for SMPS and BOB type regulators. This mode is supported by all types of regulators.`.
Example value clusters are RPMH: `RPMH_REGULATOR_MODE_RET=0`, `RPMH_REGULATOR_MODE_LPM=1`,
`RPMH_REGULATOR_MODE_AUTO=2`, `RPMH_REGULATOR_MODE_HPM=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `RPMH_REGULATOR_MODE_RET`,
`RPMH_REGULATOR_MODE_LPM`, `RPMH_REGULATOR_MODE_AUTO`, `RPMH_REGULATOR_MODE_HPM`. Test signals
include regulator schema validation, PMIC probe, regulator summary inspection, voltage/mode
transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/qcom,rpmh-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/richtek,rt5190a-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/richtek,rt5190a-regulator.h

Purpose: `richtek,rt5190a-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are RT5190A (2). Representative constants are
`RT5190A_OPMODE_AUTO`, `RT5190A_OPMODE_FPWM`, `RT5190A_OPMODE_AUTO`, `RT5190A_OPMODE_FPWM`.
Function-like helpers are none. Value shape: literal numeric range 0..1 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RICHTEK_RT5190A_REGULATOR_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RT5190A group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 15 lines long. Notable source comments include `BUCK/LDO mode constants which may be
used in devicetree properties (eg. regulator-allowed-modes). See the manufacturer's datasheet for
more information on these modes.`. Example value clusters are RT5190A: `RT5190A_OPMODE_AUTO=0`,
`RT5190A_OPMODE_FPWM=1`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `RT5190A_OPMODE_AUTO`,
`RT5190A_OPMODE_FPWM`. Test signals include regulator schema validation, PMIC probe, regulator
summary inspection, voltage/mode transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/richtek,rt5190a-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/samsung,s2mpg10-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/samsung,s2mpg10-regulator.h

Purpose: `samsung,s2mpg10-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 22 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are S2MPG10 (13), S2MPG11 (9). Representative
constants are `S2MPG10_EXTCTRL_PWREN`, `S2MPG10_EXTCTRL_PWREN_MIF`, `S2MPG10_EXTCTRL_AP_ACTIVE_N`,
`S2MPG10_EXTCTRL_CPUCL1_EN`, `S2MPG10_EXTCTRL_CPUCL1_EN2`, `S2MPG10_EXTCTRL_CPUCL2_EN`,
`S2MPG10_EXTCTRL_CPUCL2_EN2`, `S2MPG10_EXTCTRL_TPU_EN`, `...`, `S2MPG11_EXTCTRL_PWREN_MIF`,
`S2MPG11_EXTCTRL_AP_ACTIVE_N`, `S2MPG11_EXTCTRL_G3D_EN`, `S2MPG11_EXTCTRL_G3D_EN2`,
`S2MPG11_EXTCTRL_AOC_VDD`, `S2MPG11_EXTCTRL_AOC_RET`, `S2MPG11_EXTCTRL_UFS_EN`,
`S2MPG11_EXTCTRL_LDO13S_EN`. Function-like helpers are none. Value shape: 22 alias or symbol-derived
values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_SAMSUNG_S2MPG10_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `S2MPG10 group`, `S2MPG11 group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 53 lines long. Notable source comments include `Device Tree binding constants for the
Samsung S2MPG1x PMIC regulators`, `Several regulators may be controlled via external signals instead
of via software. These constants describe the possible signals for such regulators and generally
correspond to the respecitve on-chip pins. S2MPG10 regulators supporting these are: - buck1m ..
buck7m buck10m - ldo3m .. ldo19m ldo20m supports external control, but using a different set of
control signals. S2MPG11 regulators supporting these are: - buck1s .. buck3s buck5s buck8s buck9s
bucka buckd - ldo1s ldo2s ldo8s ldo13s`, `PWREN pin`, `PWREN_MIF pin`, `~AP_ACTIVE_N pin`,
`CPUCL1_EN pin`. Example value clusters are S2MPG10: `S2MPG10_EXTCTRL_PWREN=0 /* PWREN pin */`,
`S2MPG10_EXTCTRL_PWREN_MIF=1 /* PWREN_MIF pin */`, `S2MPG10_EXTCTRL_AP_ACTIVE_N=2 /* ~AP_ACTIVE_N
pin */`, `S2MPG10_EXTCTRL_CPUCL1_EN=3 /* CPUCL1_EN pin */`; S2MPG11: `S2MPG11_EXTCTRL_PWREN=0 /*
PWREN pin */`, `S2MPG11_EXTCTRL_PWREN_MIF=1 /* PWREN_MIF pin */`, `S2MPG11_EXTCTRL_AP_ACTIVE_N=2 /*
~AP_ACTIVE_N pin */`, `S2MPG11_EXTCTRL_G3D_EN=3 /* G3D_EN pin */`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `S2MPG10_EXTCTRL_PWREN`,
`S2MPG10_EXTCTRL_PWREN_MIF`, `S2MPG10_EXTCTRL_AP_ACTIVE_N`, `S2MPG10_EXTCTRL_CPUCL1_EN`,
`S2MPG10_EXTCTRL_CPUCL1_EN2`, `S2MPG10_EXTCTRL_CPUCL2_EN`, `S2MPG10_EXTCTRL_CPUCL2_EN2`,
`S2MPG10_EXTCTRL_TPU_EN`. Test signals include regulator schema validation, PMIC probe, regulator
summary inspection, voltage/mode transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/samsung,s2mpg10-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp13-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp13-regulator.h

Purpose: `st,stm32mp13-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 25 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are VOLTD (25). Representative constants are
`VOLTD_SCMI_REG11`, `VOLTD_SCMI_REG18`, `VOLTD_SCMI_USB33`, `VOLTD_SCMI_SDMMC1_IO`,
`VOLTD_SCMI_SDMMC2_IO`, `VOLTD_SCMI_VREFBUF`, `VOLTD_SCMI_STPMIC1_BUCK1`,
`VOLTD_SCMI_STPMIC1_BUCK2`, `...`, `VOLTD_SCMI_STPMIC1_BOOST`, `VOLTD_SCMI_STPMIC1_PWR_SW1`,
`VOLTD_SCMI_STPMIC1_PWR_SW2`, `VOLTD_SCMI_REGU0`, `VOLTD_SCMI_REGU1`, `VOLTD_SCMI_REGU2`,
`VOLTD_SCMI_REGU3`, `VOLTD_SCMI_REGU4`. Function-like helpers are none. Value shape: literal numeric
range 0..24 across 25 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_REGULATOR_ST_STM32MP13_REGULATOR_H`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `SCMI voltage domains identifiers`, `SOC Internal regulators`, `STPMIC1
regulators`, `External regulators`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 42 lines long. Notable source comments include `SCMI voltage domains identifiers`, `SOC
Internal regulators`, `STPMIC1 regulators`, `External regulators`,
`__DT_BINDINGS_REGULATOR_ST_STM32MP13_REGULATOR_H`. Example value clusters are VOLTD:
`VOLTD_SCMI_REG11=0`, `VOLTD_SCMI_REG18=1`, `VOLTD_SCMI_USB33=2`, `VOLTD_SCMI_SDMMC1_IO=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `VOLTD_SCMI_REG11`,
`VOLTD_SCMI_REG18`, `VOLTD_SCMI_USB33`, `VOLTD_SCMI_SDMMC1_IO`, `VOLTD_SCMI_SDMMC2_IO`,
`VOLTD_SCMI_VREFBUF`, `VOLTD_SCMI_STPMIC1_BUCK1`, `VOLTD_SCMI_STPMIC1_BUCK2`. Test signals include
regulator schema validation, PMIC probe, regulator summary inspection, voltage/mode transition
checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp13-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp15-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp15-regulator.h

Purpose: `st,stm32mp15-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 23 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are VOLTD (23). Representative constants are
`VOLTD_SCMI_REG11`, `VOLTD_SCMI_REG18`, `VOLTD_SCMI_USB33`, `VOLTD_SCMI_STPMIC1_BUCK1`,
`VOLTD_SCMI_STPMIC1_BUCK2`, `VOLTD_SCMI_STPMIC1_BUCK3`, `VOLTD_SCMI_STPMIC1_BUCK4`,
`VOLTD_SCMI_STPMIC1_LDO1`, `...`, `VOLTD_SCMI_STPMIC1_PWR_SW1`, `VOLTD_SCMI_STPMIC1_PWR_SW2`,
`VOLTD_SCMI_VREFBUF`, `VOLTD_SCMI_REGU0`, `VOLTD_SCMI_REGU1`, `VOLTD_SCMI_REGU2`,
`VOLTD_SCMI_REGU3`, `VOLTD_SCMI_REGU4`. Function-like helpers are none. Value shape: literal numeric
range 0..22 across 23 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_REGULATOR_ST_STM32MP15_REGULATOR_H`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `SCMI voltage domain identifiers`, `SOC Internal regulators`, `STPMIC1
regulators`, `External regulators`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 40 lines long. Notable source comments include `SCMI voltage domain identifiers`, `SOC
Internal regulators`, `STPMIC1 regulators`, `External regulators`,
`__DT_BINDINGS_REGULATOR_ST_STM32MP15_REGULATOR_H`. Example value clusters are VOLTD:
`VOLTD_SCMI_REG11=0`, `VOLTD_SCMI_REG18=1`, `VOLTD_SCMI_USB33=2`, `VOLTD_SCMI_STPMIC1_BUCK1=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `VOLTD_SCMI_REG11`,
`VOLTD_SCMI_REG18`, `VOLTD_SCMI_USB33`, `VOLTD_SCMI_STPMIC1_BUCK1`, `VOLTD_SCMI_STPMIC1_BUCK2`,
`VOLTD_SCMI_STPMIC1_BUCK3`, `VOLTD_SCMI_STPMIC1_BUCK4`, `VOLTD_SCMI_STPMIC1_LDO1`. Test signals
include regulator schema validation, PMIC probe, regulator summary inspection, voltage/mode
transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp15-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp25-regulator.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp25-regulator.h

Purpose: `st,stm32mp25-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 31 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are VOLTD (31). Representative constants are
`VOLTD_SCMI_VDDIO1`, `VOLTD_SCMI_VDDIO2`, `VOLTD_SCMI_VDDIO3`, `VOLTD_SCMI_VDDIO4`,
`VOLTD_SCMI_VDDIO`, `VOLTD_SCMI_UCPD`, `VOLTD_SCMI_USB33`, `VOLTD_SCMI_ADC`, `...`,
`VOLTD_SCMI_STPMIC2_LDO7`, `VOLTD_SCMI_STPMIC2_LDO8`, `VOLTD_SCMI_STPMIC2_REFDDR`,
`VOLTD_SCMI_REGU0`, `VOLTD_SCMI_REGU1`, `VOLTD_SCMI_REGU2`, `VOLTD_SCMI_REGU3`, `VOLTD_SCMI_REGU4`.
Function-like helpers are none. Value shape: literal numeric range 0..30 across 31 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_REGULATOR_ST_STM32MP25_REGULATOR_H`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `SCMI voltage domains identifiers`, `SOC Internal regulators`, `STPMIC2
regulators`, `External regulators`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 48 lines long. Notable source comments include `SCMI voltage domains identifiers`, `SOC
Internal regulators`, `STPMIC2 regulators`, `External regulators`,
`__DT_BINDINGS_REGULATOR_ST_STM32MP25_REGULATOR_H`. Example value clusters are VOLTD:
`VOLTD_SCMI_VDDIO1=0`, `VOLTD_SCMI_VDDIO2=1`, `VOLTD_SCMI_VDDIO3=2`, `VOLTD_SCMI_VDDIO4=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `VOLTD_SCMI_VDDIO1`,
`VOLTD_SCMI_VDDIO2`, `VOLTD_SCMI_VDDIO3`, `VOLTD_SCMI_VDDIO4`, `VOLTD_SCMI_VDDIO`,
`VOLTD_SCMI_UCPD`, `VOLTD_SCMI_USB33`, `VOLTD_SCMI_ADC`. Test signals include regulator schema
validation, PMIC probe, regulator summary inspection, voltage/mode transition checks, and
suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp25-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/ti,tps62864.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/ti,tps62864.h

Purpose: `ti,tps62864.h` is a Devicetree binding header for a regulator provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are TPS62864 (2). Representative constants are
`TPS62864_MODE_NORMAL`, `TPS62864_MODE_FPWM`, `TPS62864_MODE_NORMAL`, `TPS62864_MODE_FPWM`.
Function-like helpers are none. Value shape: literal numeric range 0..1 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_TI_TPS62864_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `TPS62864 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 9 lines long. Notable source comments include none. Example value clusters are TPS62864:
`TPS62864_MODE_NORMAL=0`, `TPS62864_MODE_FPWM=1`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `TPS62864_MODE_NORMAL`,
`TPS62864_MODE_FPWM`. Test signals include regulator schema validation, PMIC probe, regulator
summary inspection, voltage/mode transition checks, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/regulator/ti,tps62864.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s500-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s500-reset.h

Purpose: `actions,s500-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 54 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_USB2 (2), RESET_DMAC (1), RESET_NORIF (1),
RESET_DDR (1), RESET_NANDC (1), RESET_SD0 (1), RESET_SD1 (1), RESET_PCM1 (1), RESET_DE (1),
RESET_LCD (1). Representative constants are `RESET_DMAC`, `RESET_NORIF`, `RESET_DDR`, `RESET_NANDC`,
`RESET_SD0`, `RESET_SD1`, `RESET_PCM1`, `RESET_DE`, `...`, `RESET_WD0RESET`, `RESET_WD1RESET`,
`RESET_WD2RESET`, `RESET_WD3RESET`, `RESET_DBG0RESET`, `RESET_DBG1RESET`, `RESET_DBG2RESET`,
`RESET_DBG3RESET`. Function-like helpers are none. Value shape: literal numeric range 0..53 across
54 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_ACTIONS_S500_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET_USB2 group`, `RESET_DMAC group`, `RESET_NORIF group`, `RESET_DDR group`, `RESET_NANDC
group`, `RESET_SD0 group`, `RESET_SD1 group`, `RESET_PCM1 group`, `RESET_DE group`, `RESET_LCD
group`, `RESET_SD2 group`, `RESET_DSI group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 67 lines long. Notable source comments include `Device Tree binding constants for
Actions Semi S500 Reset Management Unit`, `__DT_BINDINGS_ACTIONS_S500_RESET_H`. Example value
clusters are RESET_USB2: `RESET_USB2_0=23`, `RESET_USB2_1=45`; RESET_DMAC: `RESET_DMAC=0`;
RESET_NORIF: `RESET_NORIF=1`; RESET_DDR: `RESET_DDR=2`; RESET_NANDC: `RESET_NANDC=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_DMAC`,
`RESET_NORIF`, `RESET_DDR`, `RESET_NANDC`, `RESET_SD0`, `RESET_SD1`, `RESET_PCM1`, `RESET_DE`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s500-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s700-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s700-reset.h

Purpose: `actions,s700-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 23 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_AUDIO (1), RESET_CSI (1), RESET_DE (1),
RESET_DSI (1), RESET_GPIO (1), RESET_I2C0 (1), RESET_I2C1 (1), RESET_I2C2 (1), RESET_I2C3 (1),
RESET_KEY (1). Representative constants are `RESET_AUDIO`, `RESET_CSI`, `RESET_DE`, `RESET_DSI`,
`RESET_GPIO`, `RESET_I2C0`, `RESET_I2C1`, `RESET_I2C2`, `...`, `RESET_SPI3`, `RESET_UART0`,
`RESET_UART1`, `RESET_UART2`, `RESET_UART3`, `RESET_UART4`, `RESET_UART5`, `RESET_UART6`. Function-
like helpers are none. Value shape: literal numeric range 0..22 across 23 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_ACTIONS_S700_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET_AUDIO group`, `RESET_CSI group`, `RESET_DE group`, `RESET_DSI group`, `RESET_GPIO group`,
`RESET_I2C0 group`, `RESET_I2C1 group`, `RESET_I2C2 group`, `RESET_I2C3 group`, `RESET_KEY group`,
`RESET_LCD0 group`, `RESET_SI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 34 lines long. Notable source comments include `__DT_BINDINGS_ACTIONS_S700_RESET_H`.
Example value clusters are RESET_AUDIO: `RESET_AUDIO=0`; RESET_CSI: `RESET_CSI=1`; RESET_DE:
`RESET_DE=2`; RESET_DSI: `RESET_DSI=3`; RESET_GPIO: `RESET_GPIO=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AUDIO`,
`RESET_CSI`, `RESET_DE`, `RESET_DSI`, `RESET_GPIO`, `RESET_I2C0`, `RESET_I2C1`, `RESET_I2C2`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s700-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s900-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s900-reset.h

Purpose: `actions,s900-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 54 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_DDR (2), RESET_GPU3D (2), RESET_CHIPID (1),
RESET_CPU (1), RESET_SRAMI (1), RESET_DMAC (1), RESET_GPIO (1), RESET_BISP (1), RESET_CSI0 (1),
RESET_CSI1 (1). Representative constants are `RESET_CHIPID`, `RESET_CPU_SCNT`, `RESET_SRAMI`,
`RESET_DDR_CTL_PHY`, `RESET_DMAC`, `RESET_GPIO`, `RESET_BISP_AXI`, `RESET_CSI0`, `...`,
`RESET_PCM0`, `RESET_SE`, `RESET_GIC`, `RESET_DDR_CTL_PHY_AXI`, `RESET_CMU_DDR`, `RESET_DMM`,
`RESET_HDCP2TX`, `RESET_ETHERNET`. Function-like helpers are none. Value shape: literal numeric
range 0..53 across 54 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_ACTIONS_S900_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET_DDR group`, `RESET_GPU3D group`, `RESET_CHIPID group`, `RESET_CPU group`, `RESET_SRAMI
group`, `RESET_DMAC group`, `RESET_GPIO group`, `RESET_BISP group`, `RESET_CSI0 group`, `RESET_CSI1
group`, `RESET_DE group`, `RESET_DSI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 65 lines long. Notable source comments include `__DT_BINDINGS_ACTIONS_S900_RESET_H`.
Example value clusters are RESET_DDR: `RESET_DDR_CTL_PHY=3`, `RESET_DDR_CTL_PHY_AXI=49`;
RESET_GPU3D: `RESET_GPU3D_PA=11`, `RESET_GPU3D_PB=12`; RESET_CHIPID: `RESET_CHIPID=0`; RESET_CPU:
`RESET_CPU_SCNT=1`; RESET_SRAMI: `RESET_SRAMI=2`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_CHIPID`,
`RESET_CPU_SCNT`, `RESET_SRAMI`, `RESET_DDR_CTL_PHY`, `RESET_DMAC`, `RESET_GPIO`, `RESET_BISP_AXI`,
`RESET_CSI0`. Test signals include DTS compile checks, reset-controller probe, driver reset/deassert
paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/actions,s900-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/airoha,en7523-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/airoha,en7523-reset.h

Purpose: `airoha,en7523-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 42 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EN7523 (42). Representative constants are
`EN7523_XPON_PHY_RST`, `EN7523_XSI_MAC_RST`, `EN7523_XSI_PHY_RST`, `EN7523_NPU_RST`,
`EN7523_I2S_RST`, `EN7523_TRNG_RST`, `EN7523_TRNG_MSTART_RST`, `EN7523_DUAL_HSI0_RST`, `...`,
`EN7523_FE_RST`, `EN7523_USB_HOST_P0_RST`, `EN7523_GSW_RST`, `EN7523_SFC2_PCM_RST`,
`EN7523_PCIE0_RST`, `EN7523_PCIE1_RST`, `EN7523_PCIE_HB_RST`, `EN7523_XPON_MAC_RST`. Function-like
helpers are none. Value shape: literal numeric range 0..41 across 42 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_CONTROLLER_AIROHA_EN7523_H_`; after preprocessing, DTS C-preprocessor users and
C drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RST_CTRL2`, `RST_CTRL1`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 61 lines long. Notable source comments include `based on include/dt-
bindings/reset/airoha,en7581-reset.h by Lorenzo Bianconi <lorenzo@kernel.org>`, `RST_CTRL2`,
`RST_CTRL1`, `__DT_BINDINGS_RESET_CONTROLLER_AIROHA_EN7523_H_`. Example value clusters are EN7523:
`EN7523_XPON_PHY_RST=0`, `EN7523_XSI_MAC_RST=1`, `EN7523_XSI_PHY_RST=2`, `EN7523_NPU_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `EN7523_XPON_PHY_RST`,
`EN7523_XSI_MAC_RST`, `EN7523_XSI_PHY_RST`, `EN7523_NPU_RST`, `EN7523_I2S_RST`, `EN7523_TRNG_RST`,
`EN7523_TRNG_MSTART_RST`, `EN7523_DUAL_HSI0_RST`. Test signals include DTS compile checks, reset-
controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/airoha,en7523-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/airoha,en7581-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/airoha,en7581-reset.h

Purpose: `airoha,en7581-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 53 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EN7581 (53). Representative constants are
`EN7581_XPON_PHY_RST`, `EN7581_CPU_TIMER2_RST`, `EN7581_HSUART_RST`, `EN7581_UART4_RST`,
`EN7581_UART5_RST`, `EN7581_I2C2_RST`, `EN7581_XSI_MAC_RST`, `EN7581_XSI_PHY_RST`, `...`,
`EN7581_USB_HOST_P0_RST`, `EN7581_GSW_RST`, `EN7581_SFC2_PCM_RST`, `EN7581_PCIE0_RST`,
`EN7581_PCIE1_RST`, `EN7581_CPU_TIMER_RST`, `EN7581_PCIE_HB_RST`, `EN7581_XPON_MAC_RST`. Function-
like helpers are none. Value shape: literal numeric range 0..52 across 53 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_CONTROLLER_AIROHA_EN7581_H_`; after preprocessing, DTS C-preprocessor users and
C drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RST_CTRL2`, `RST_CTRL1`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 66 lines long. Notable source comments include `RST_CTRL2`, `RST_CTRL1`,
`__DT_BINDINGS_RESET_CONTROLLER_AIROHA_EN7581_H_`. Example value clusters are EN7581:
`EN7581_XPON_PHY_RST=0`, `EN7581_CPU_TIMER2_RST=1`, `EN7581_HSUART_RST=2`, `EN7581_UART4_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `EN7581_XPON_PHY_RST`,
`EN7581_CPU_TIMER2_RST`, `EN7581_HSUART_RST`, `EN7581_UART4_RST`, `EN7581_UART5_RST`,
`EN7581_I2C2_RST`, `EN7581_XSI_MAC_RST`, `EN7581_XSI_PHY_RST`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/airoha,en7581-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-a10.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-a10.h

Purpose: `altr,rst-mgr-a10.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 72 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EMAC0 (2), EMAC1 (2), EMAC2 (2), USB0 (2), USB1 (2),
NAND (2), QSPI (2), SDMMC (2), OCRAM (2), CPU0 (1). Representative constants are `CPU0_RESET`,
`CPU1_RESET`, `WDS_RESET`, `SCUPER_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `EMAC2_RESET`,
`USB0_RESET`, `...`, `CLKMGRCOLD_RESET`, `S2FCOLD_RESET`, `TIMESTAMPCOLD_RESET`, `TAPCOLD_RESET`,
`HMCCOLD_RESET`, `IOMGRCOLD_RESET`, `NRSTPINOE_RESET`, `DBG_RESET`. Function-like helpers are none.
Value shape: literal numeric range 0..224 across 72 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_ALTR_RST_MGR_A10_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MPUMODRST`, `PER0MODRST`, `55 is empty`, `PER1MODRST`, `70-71 is reserved`, `77-79 is
reserved`, `82-87 is reserved`, `BRGMODRST`, `SYSMODRST`, `130 is reserved`, `COLDMODRST`, `161-162
is reserved`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 102 lines long. Notable source comments include `MPUMODRST`, `PER0MODRST`, `55 is
empty`, `PER1MODRST`, `70-71 is reserved`, `77-79 is reserved`. Example value clusters are EMAC0:
`EMAC0_RESET=32`, `EMAC0_OCP_RESET=40`; EMAC1: `EMAC1_RESET=33`, `EMAC1_OCP_RESET=41`; EMAC2:
`EMAC2_RESET=34`, `EMAC2_OCP_RESET=42`; USB0: `USB0_RESET=35`, `USB0_OCP_RESET=43`; USB1:
`USB1_RESET=36`, `USB1_OCP_RESET=44`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CPU0_RESET`,
`CPU1_RESET`, `WDS_RESET`, `SCUPER_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `EMAC2_RESET`,
`USB0_RESET`. Test signals include DTS compile checks, reset-controller probe, driver reset/deassert
paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-a10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-a10sr.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-a10sr.h

Purpose: `altr,rst-mgr-a10sr.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are A10SR (6). Representative constants are
`A10SR_RESET_ENET_HPS`, `A10SR_RESET_PCIE`, `A10SR_RESET_FILE`, `A10SR_RESET_BQSPI`,
`A10SR_RESET_USB`, `A10SR_RESET_NUM`, `A10SR_RESET_ENET_HPS`, `A10SR_RESET_PCIE`,
`A10SR_RESET_FILE`, `A10SR_RESET_BQSPI`, `A10SR_RESET_USB`, `A10SR_RESET_NUM`. Function-like helpers
are none. Value shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_ALTR_RST_MGR_A10SR_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `Peripheral PHY resets`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 22 lines long. Notable source comments include `Reset binding definitions for Altera
Arria10 MAX5 System Resource Chip Adapted from altr,rst-mgr-a10.h`, `Peripheral PHY resets`. Example
value clusters are A10SR: `A10SR_RESET_ENET_HPS=0`, `A10SR_RESET_PCIE=1`, `A10SR_RESET_FILE=2`,
`A10SR_RESET_BQSPI=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `A10SR_RESET_ENET_HPS`,
`A10SR_RESET_PCIE`, `A10SR_RESET_FILE`, `A10SR_RESET_BQSPI`, `A10SR_RESET_USB`, `A10SR_RESET_NUM`.
Test signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-a10sr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-s10.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-s10.h

Purpose: `altr,rst-mgr-s10.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 68 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EMAC0 (2), EMAC1 (2), EMAC2 (2), USB0 (2), USB1 (2),
NAND (2), SDMMC (2), CPU0 (1), CPU1 (1), CPU2 (1). Representative constants are `CPU0_RESET`,
`CPU1_RESET`, `CPU2_RESET`, `CPU3_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `EMAC2_RESET`, `USB0_RESET`,
`...`, `CPUPO0_RESET`, `CPUPO1_RESET`, `CPUPO2_RESET`, `CPUPO3_RESET`, `L2_RESET`, `DBG_RESET`,
`CSDAP_RESET`, `TAP_RESET`. Function-like helpers are none. Value shape: literal numeric range
0..256 across 68 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_ALTR_RST_MGR_S10_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MPUMODRST`, `PER0MODRST`, `38 is empty`, `46 is empty`, `55 is empty`, `PER1MODRST`, `79 is
empty`, `82-87 is empty`, `BRGMODRST`, `COLDMODRST`, `164-167 is empty`, `DBGMODRST`, which is the
intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 100 lines long. Notable source comments include `derived from Steffen Trumtrar's
"altr,rst-mgr-a10.h"`, `MPUMODRST`, `PER0MODRST`, `38 is empty`, `46 is empty`, `55 is empty`.
Example value clusters are EMAC0: `EMAC0_RESET=32`, `EMAC0_OCP_RESET=40`; EMAC1: `EMAC1_RESET=33`,
`EMAC1_OCP_RESET=41`; EMAC2: `EMAC2_RESET=34`, `EMAC2_OCP_RESET=42`; USB0: `USB0_RESET=35`,
`USB0_OCP_RESET=43`; USB1: `USB1_RESET=36`, `USB1_OCP_RESET=44`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CPU0_RESET`,
`CPU1_RESET`, `CPU2_RESET`, `CPU3_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `EMAC2_RESET`, `USB0_RESET`.
Test signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr-s10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr.h

Purpose: `altr,rst-mgr.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 63 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are CPU0 (1), CPU1 (1), WDS_RESET (1), SCUPER (1),
L2_RESET (1), EMAC0 (1), EMAC1 (1), USB0 (1), USB1 (1), NAND (1). Representative constants are
`CPU0_RESET`, `CPU1_RESET`, `WDS_RESET`, `SCUPER_RESET`, `L2_RESET`, `EMAC0_RESET`, `EMAC1_RESET`,
`USB0_RESET`, `...`, `TIMESTAMPCOLD_RESET`, `CLKMGRCOLD_RESET`, `SCANMGR_RESET`,
`FRZCTRLCOLD_RESET`, `SYSDBG_RESET`, `DBG_RESET`, `TAPCOLD_RESET`, `SDRCOLD_RESET`. Function-like
helpers are none. Value shape: literal numeric range 0..144 across 63 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_ALTR_RST_MGR_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MPUMODRST`, `PERMODRST`, `PER2MODRST`, `BRGMODRST`, `MISCMODRST`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 82 lines long. Notable source comments include `MPUMODRST`, `PERMODRST`, `PER2MODRST`,
`BRGMODRST`, `MISCMODRST`. Example value clusters are CPU0: `CPU0_RESET=0`; CPU1: `CPU1_RESET=1`;
WDS_RESET: `WDS_RESET=2`; SCUPER: `SCUPER_RESET=3`; L2_RESET: `L2_RESET=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CPU0_RESET`,
`CPU1_RESET`, `WDS_RESET`, `SCUPER_RESET`, `L2_RESET`, `EMAC0_RESET`, `EMAC1_RESET`, `USB0_RESET`.
Test signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/altr,rst-mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,c3-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,c3-reset.h

Purpose: `amlogic,c3-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 76 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_BRG (11), RESET_CVE (7), RESET_PWM (7),
RESET_ISP (6), RESET_UART (6), RESET_I2C (5), RESET_VC9000E (3), RESET_SD (3), RESET_MIPI (2),
RESET_DOS (2). Representative constants are `RESET_USBCTRL`, `RESET_USBPHY20`, `RESET_USB2DRD`,
`RESET_MIPI_DSI_HOST`, `RESET_MIPI_DSI_PHY`, `RESET_GE2D`, `RESET_DWAP`, `RESET_AUDIO`, `...`,
`RESET_BRG_NIC_VAPB`, `RESET_BRG_NIC_SDIO_B`, `RESET_BRG_NIC_SDIO_A`, `RESET_BRG_NIC_EMMC`,
`RESET_BRG_NIC_DSU`, `RESET_BRG_NIC_SYSCLK`, `RESET_BRG_NIC_MAIN`, `RESET_BRG_NIC_ALL`. Function-
like helpers are none. Value shape: literal numeric range 4..191 across 76 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_C3_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`RESET0`, `0-3`, `5-7`, `13-20`, `23-31`, `RESET1`, `33-34`, `39-46`, `54-63`, `RESET2`, `68-72`,
`76-79`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 119 lines long. Notable source comments include `RESET0`, `0-3`, `5-7`, `9`, `13-20`,
`23-31`. Example value clusters are RESET_BRG: `RESET_BRG_NIC_NNA=173`,
`RESET_BRG_MUX_NIC_MAIN=174`, `RESET_BRG_AO_NIC_ALL=175`, `RESET_BRG_NIC_VAPB=184`; RESET_CVE:
`RESET_CVE_NIC_GPV=104`, `RESET_CVE_NIC_MAIN=105`, `RESET_CVE_NIC_GE2D=106`, `RESET_CVE_NIC_DW=106`;
RESET_PWM: `RESET_PWM_AB=129`, `RESET_PWM_CD=130`, `RESET_PWM_EF=131`, `RESET_PWM_GH=132`;
RESET_ISP: `RESET_ISP=49`, `RESET_ISP_NIC_GPV=96`, `RESET_ISP_NIC_MAIN=97`, `RESET_ISP_NIC_VCLK=98`;
RESET_UART: `RESET_UART_A=138`, `RESET_UART_B=139`, `RESET_UART_C=140`, `RESET_UART_D=141`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_USBCTRL`,
`RESET_USBPHY20`, `RESET_USB2DRD`, `RESET_MIPI_DSI_HOST`, `RESET_MIPI_DSI_PHY`, `RESET_GE2D`,
`RESET_DWAP`, `RESET_AUDIO`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,c3-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-a1-audio-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-a1-audio-reset.h

Purpose: `amlogic,meson-a1-audio-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 23 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are AUD_RESET (17), AUD_VAD (6). Representative
constants are `AUD_RESET_DDRARB`, `AUD_RESET_TDMIN_A`, `AUD_RESET_TDMIN_B`, `AUD_RESET_TDMIN_LB`,
`AUD_RESET_LOOPBACK`, `AUD_RESET_TDMOUT_A`, `AUD_RESET_TDMOUT_B`, `AUD_RESET_FRDDR_A`, `...`,
`AUD_RESET_TOACODEC`, `AUD_RESET_CLKTREE`, `AUD_VAD_RESET_DDRARB`, `AUD_VAD_RESET_PDM`,
`AUD_VAD_RESET_TDMIN_VAD`, `AUD_VAD_RESET_TODDR_VAD`, `AUD_VAD_RESET_TOVAD`,
`AUD_VAD_RESET_CLKTREE`. Function-like helpers are none. Value shape: literal numeric range 0..31
across 23 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_A1_AUDIO_RESET_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `AUD_RESET group`, `AUD_VAD group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 36 lines long. Notable source comments include
`_DT_BINDINGS_AMLOGIC_MESON_A1_AUDIO_RESET_H`. Example value clusters are AUD_RESET:
`AUD_RESET_DDRARB=0`, `AUD_RESET_TDMIN_A=1`, `AUD_RESET_TDMIN_B=2`, `AUD_RESET_TDMIN_LB=3`; AUD_VAD:
`AUD_VAD_RESET_DDRARB=0`, `AUD_VAD_RESET_PDM=1`, `AUD_VAD_RESET_TDMIN_VAD=2`,
`AUD_VAD_RESET_TODDR_VAD=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `AUD_RESET_DDRARB`,
`AUD_RESET_TDMIN_A`, `AUD_RESET_TDMIN_B`, `AUD_RESET_TDMIN_LB`, `AUD_RESET_LOOPBACK`,
`AUD_RESET_TDMOUT_A`, `AUD_RESET_TDMOUT_B`, `AUD_RESET_FRDDR_A`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-a1-audio-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-a1-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-a1-reset.h

Purpose: `amlogic,meson-a1-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 42 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_I2C (7), RESET_PWM (3), RESET_UART (3),
RESET_AM2AXI (2), RESET_AUDIO (2), RESET_NIC (2), RESET_PSRAM (1), RESET_PAD (1), RESET_TEMP (1),
RESET_SPICC (1). Representative constants are `RESET_AM2AXI_VAD`, `RESET_PSRAM`, `RESET_PAD_CTRL`,
`RESET_TEMP_SENSOR`, `RESET_AM2AXI_DEV`, `RESET_SPICC_A`, `RESET_MSR_CLK`, `RESET_AUDIO`, `...`,
`RESET_RAMB`, `RESET_ROM`, `RESET_SPIFC`, `RESET_GIC`, `RESET_UART_C`, `RESET_UART_B`,
`RESET_UART_A`, `RESET_OSC_RING`. Function-like helpers are none. Value shape: literal numeric range
1..59 across 42 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_A1_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET0`, `2-3`, `30-31`, `RESET1`, `39-41`, `51-52`, `60-63`, `RESET2`, `64-95`, which is the
intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 74 lines long. Notable source comments include `RESET0`, `0`, `2-3`, `6`, `9`, `20`.
Example value clusters are RESET_I2C: `RESET_I2C_S_A=22`, `RESET_I2C_M_D=24`, `RESET_I2C_M_C=25`,
`RESET_I2C_M_B=26`; RESET_PWM: `RESET_PWM_EF=17`, `RESET_PWM_CD=18`, `RESET_PWM_AB=19`; RESET_UART:
`RESET_UART_C=56`, `RESET_UART_B=57`, `RESET_UART_A=58`; RESET_AM2AXI: `RESET_AM2AXI_VAD=1`,
`RESET_AM2AXI_DEV=8`; RESET_AUDIO: `RESET_AUDIO=12`, `RESET_AUDIO_VAD=15`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AM2AXI_VAD`,
`RESET_PSRAM`, `RESET_PAD_CTRL`, `RESET_TEMP_SENSOR`, `RESET_AM2AXI_DEV`, `RESET_SPICC_A`,
`RESET_MSR_CLK`, `RESET_AUDIO`. Test signals include DTS compile checks, reset-controller probe,
driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-a1-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-axg-audio-arb.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-axg-audio-arb.h

Purpose: `amlogic,meson-axg-audio-arb.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are AXG_ARB (8). Representative constants are
`AXG_ARB_TODDR_A`, `AXG_ARB_TODDR_B`, `AXG_ARB_TODDR_C`, `AXG_ARB_FRDDR_A`, `AXG_ARB_FRDDR_B`,
`AXG_ARB_FRDDR_C`, `AXG_ARB_TODDR_D`, `AXG_ARB_FRDDR_D`, `AXG_ARB_TODDR_A`, `AXG_ARB_TODDR_B`,
`AXG_ARB_TODDR_C`, `AXG_ARB_FRDDR_A`, `AXG_ARB_FRDDR_B`, `AXG_ARB_FRDDR_C`, `AXG_ARB_TODDR_D`,
`AXG_ARB_FRDDR_D`. Function-like helpers are none. Value shape: literal numeric range 0..7 across 8
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_AXG_AUDIO_ARB_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `AXG_ARB group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 19 lines long. Notable source comments include
`_DT_BINDINGS_AMLOGIC_MESON_AXG_AUDIO_ARB_H`. Example value clusters are AXG_ARB:
`AXG_ARB_TODDR_A=0`, `AXG_ARB_TODDR_B=1`, `AXG_ARB_TODDR_C=2`, `AXG_ARB_FRDDR_A=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `AXG_ARB_TODDR_A`,
`AXG_ARB_TODDR_B`, `AXG_ARB_TODDR_C`, `AXG_ARB_FRDDR_A`, `AXG_ARB_FRDDR_B`, `AXG_ARB_FRDDR_C`,
`AXG_ARB_TODDR_D`, `AXG_ARB_FRDDR_D`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-axg-audio-arb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-axg-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-axg-reset.h

Purpose: `amlogic,meson-axg-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 66 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_SYS (14), RESET_PERIPHS (7), RESET_USB (5),
RESET_PCIE (4), RESET_AHB (3), RESET_DDR (2), RESET_VCBUS (2), RESET_AO (2), RESET_SD (2),
RESET_AUDIO (2). Representative constants are `RESET_HIU`, `RESET_PCIE_A`, `RESET_PCIE_B`,
`RESET_DDR_TOP`, `RESET_VIU`, `RESET_PCIE_PHY`, `RESET_PCIE_APB`, `RESET_VENC`, `...`,
`RESET_USB_DDR_0`, `RESET_USB_DDR_1`, `RESET_USB_DDR_2`, `RESET_USB_DDR_3`, `RESET_DEVICE_MMC_ARB`,
`RESET_VID_LOCK`, `RESET_A9_DMC_PIPEL`, `RESET_DMC_VPU_PIPEL`. Function-like helpers are none. Value
shape: literal numeric range 0..233 across 66 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_AXG_RESET_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RESET0`, `18-21`, `28-31`, `RESET1`, `61-63`, `RESET2`, `71-76`, `78-95`, `RESET3`,
`97-127`, `RESET4`, `128`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 123 lines long. Notable source comments include `RESET0`, `4`, `8`, `9`, `12`, `14`.
Example value clusters are RESET_SYS: `RESET_SYS_CPU_CAPB3=22`, `RESET_SYS_CPU_0=48`,
`RESET_SYS_CPU_1=49`, `RESET_SYS_CPU_2=50`; RESET_PERIPHS: `RESET_PERIPHS_GENERAL=192`,
`RESET_PERIPHS_SPICC=193`, `RESET_PERIPHS_I2C_MASTER_0=196`, `RESET_PERIPHS_UART_0=201`; RESET_USB:
`RESET_USB_OTG=34`, `RESET_USB_DDR_0=224`, `RESET_USB_DDR_1=225`, `RESET_USB_DDR_2=226`; RESET_PCIE:
`RESET_PCIE_A=1`, `RESET_PCIE_B=2`, `RESET_PCIE_PHY=6`, `RESET_PCIE_APB=7`; RESET_AHB:
`RESET_AHB_CNTL=24`, `RESET_AHB_DATA=25`, `RESET_AHB_SRAM=38`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_HIU`,
`RESET_PCIE_A`, `RESET_PCIE_B`, `RESET_DDR_TOP`, `RESET_VIU`, `RESET_PCIE_PHY`, `RESET_PCIE_APB`,
`RESET_VENC`. Test signals include DTS compile checks, reset-controller probe, driver reset/deassert
paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-axg-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-g12a-audio-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-g12a-audio-reset.h

Purpose: `amlogic,meson-g12a-audio-reset.h` is a Devicetree binding header for a reset-controller provider.
It exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 39 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are AUD_RESET (39). Representative constants are
`AUD_RESET_PDM`, `AUD_RESET_TDMIN_A`, `AUD_RESET_TDMIN_B`, `AUD_RESET_TDMIN_C`,
`AUD_RESET_TDMIN_LB`, `AUD_RESET_LOOPBACK`, `AUD_RESET_TODDR_A`, `AUD_RESET_TODDR_B`, `...`,
`AUD_RESET_FRHDMIRX`, `AUD_RESET_FRDDR_D`, `AUD_RESET_TODDR_D`, `AUD_RESET_LOOPBACK_B`,
`AUD_RESET_EARCTX`, `AUD_RESET_EARCRX`, `AUD_RESET_FRDDR_E`, `AUD_RESET_TODDR_E`. Function-like
helpers are none. Value shape: literal numeric range 0..38 across 39 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_G12A_AUDIO_RESET_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `SM1 added resets`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 53 lines long. Notable source comments include `SM1 added resets`. Example value
clusters are AUD_RESET: `AUD_RESET_PDM=0`, `AUD_RESET_TDMIN_A=1`, `AUD_RESET_TDMIN_B=2`,
`AUD_RESET_TDMIN_C=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `AUD_RESET_PDM`,
`AUD_RESET_TDMIN_A`, `AUD_RESET_TDMIN_B`, `AUD_RESET_TDMIN_C`, `AUD_RESET_TDMIN_LB`,
`AUD_RESET_LOOPBACK`, `AUD_RESET_TODDR_A`, `AUD_RESET_TODDR_B`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-g12a-audio-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-g12a-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-g12a-reset.h

Purpose: `amlogic,meson-g12a-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 91 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_DEMUX (8), RESET_USB (7), RESET_PARSER (4),
RESET_I2C (4), RESET_PCIE (3), RESET_HDMITX (3), RESET_DVALIN (3), RESET_AHB (3), RESET_SD (3),
RESET_TS (3). Representative constants are `RESET_HIU`, `RESET_DOS`, `RESET_VIU`, `RESET_AFIFO`,
`RESET_VID_PLL_DIV`, `RESET_VENC`, `RESET_ASSIST`, `RESET_PCIE_CTRL_A`, `...`,
`RESET_DVALIN_DMC_PIPL`, `RESET_VID_LOCK`, `RESET_NIC_DMC_PIPL`, `RESET_DMC_VPU_PIPL`,
`RESET_GE2D_DMC_PIPL`, `RESET_HCODEC_DMC_PIPL`, `RESET_WAVE420_DMC_PIPL`, `RESET_HEVCF_DMC_PIPL`.
Function-like helpers are none. Value shape: literal numeric range 0..237 across 91 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_G12A_RESET_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RESET0`, `3-4`, `8-9`, `27-31`, `RESET1`, `50-60`, `62-63`, `RESET2`, `80-95`,
`RESET3`, `96-95`, `112-127`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 139 lines long. Notable source comments include `RESET0`, `1`, `3-4`, `8-9`, `18`, `22`.
Example value clusters are RESET_DEMUX: `RESET_DEMUX=33`, `RESET_DEMUX_TOP=105`,
`RESET_DEMUX_DES_PL=106`, `RESET_DEMUX_S2P_0=107`; RESET_USB: `RESET_USB=34`, `RESET_USB_PHY20=48`,
`RESET_USB_PHY21=49`, `RESET_USB_DDR_0=224`; RESET_PARSER: `RESET_PARSER=40`, `RESET_PARSER_REG=71`,
`RESET_PARSER_FETCH=72`, `RESET_PARSER_TOP=74`; RESET_I2C: `RESET_I2C_M1=142`, `RESET_I2C_M2=143`,
`RESET_I2C_M0=196`, `RESET_I2C_M3=206`; RESET_PCIE: `RESET_PCIE_CTRL_A=12`, `RESET_PCIE_PHY=14`,
`RESET_PCIE_APB=15`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_HIU`,
`RESET_DOS`, `RESET_VIU`, `RESET_AFIFO`, `RESET_VID_PLL_DIV`, `RESET_VENC`, `RESET_ASSIST`,
`RESET_PCIE_CTRL_A`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-g12a-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-gxbb-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-gxbb-reset.h

Purpose: `amlogic,meson-gxbb-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 115 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_SYS (16), RESET_PERIPHS (13), RESET_DEMUX (8),
RESET_USB (5), RESET_PARSER (5), RESET_AHB (4), RESET_MIPI (4), RESET_SD (3), RESET_DOS (2),
RESET_DDR (2). Representative constants are `RESET_HIU`, `RESET_DOS_RESET`, `RESET_DDR_TOP`,
`RESET_DCU_RESET`, `RESET_VIU`, `RESET_AIU`, `RESET_VID_PLL_DIV`, `RESET_PMUX`, `...`,
`RESET_UART_SLIP`, `RESET_USB_DDR_0`, `RESET_USB_DDR_1`, `RESET_USB_DDR_2`, `RESET_USB_DDR_3`,
`RESET_DEVICE_MMC_ARB`, `RESET_VID_LOCK`, `RESET_A9_DMC_PIPEL`. Function-like helpers are none.
Value shape: literal numeric range 0..232 across 115 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_GXBB_RESET_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RESET0`, `RESET1`, `RESET2`, `80-95`, `RESET3`, `103`, `112-127`, `RESET4`, `128`,
`129`, `130`, `131`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 161 lines long. Notable source comments include `RESET0`, `1`, `8`, `14`, `15`,
`RESET1`. Example value clusters are RESET_SYS: `RESET_SYS_CPU_CAPB3=22`, `RESET_SYS_CPU_0=48`,
`RESET_SYS_CPU_1=49`, `RESET_SYS_CPU_2=50`; RESET_PERIPHS: `RESET_PERIPHS_GENERAL=192`,
`RESET_PERIPHS_SPICC=193`, `RESET_PERIPHS_SMART_CARD=194`, `RESET_PERIPHS_SAR_ADC=195`; RESET_DEMUX:
`RESET_DEMUX=33`, `RESET_DEMUX_TOP=105`, `RESET_DEMUX_DES=106`, `RESET_DEMUX_S2P_0=107`; RESET_USB:
`RESET_USB_OTG=34`, `RESET_USB_DDR_0=224`, `RESET_USB_DDR_1=225`, `RESET_USB_DDR_2=226`;
RESET_PARSER: `RESET_PARSER=40`, `RESET_PARSER_REG=71`, `RESET_PARSER_FETCH=72`,
`RESET_PARSER_CTL=73`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_HIU`,
`RESET_DOS_RESET`, `RESET_DDR_TOP`, `RESET_DCU_RESET`, `RESET_VIU`, `RESET_AIU`,
`RESET_VID_PLL_DIV`, `RESET_PMUX`. Test signals include DTS compile checks, reset-controller probe,
driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-gxbb-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-s4-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-s4-reset.h

Purpose: `amlogic,meson-s4-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 81 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_BRG (16), RESET_I2C (6), RESET_PWM (5),
RESET_UART (5), RESET_USB (4), RESET_VID (2), RESET_MALI (2), RESET_DDR (2), RESET_DOS (2),
RESET_TEMPSENSOR (2). Representative constants are `RESET_USB_DDR0`, `RESET_USB_DDR1`,
`RESET_USB_DDR2`, `RESET_USB_DDR3`, `RESET_USBCTRL`, `RESET_USBPHY20`, `RESET_USBPHY21`,
`RESET_HDMITX_APB`, `...`, `RESET_BRG_HEVCF_PIPL1`, `RESET_BRG_HEVCB_PIPL1`, `RESET_RAMA`,
`RESET_BRG_NIC_VAPB`, `RESET_BRG_NIC_DSU`, `RESET_BRG_NIC_SYSCLK`, `RESET_BRG_NIC_MAIN`,
`RESET_BRG_NIC_ALL`. Function-like helpers are none. Value shape: literal numeric range 0..191
across 81 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_S4_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET0`, `5-7`, `10-15`, `RESET1`, `39-47`, `49-51`, `53-63`, `RESET2`, `68-71`, `76-79`,
`83-87`, `92-95`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 125 lines long. Notable source comments include `RESET0`, `5-7`, `10-15`, `RESET1`,
`39-47`, `49-51`. Example value clusters are RESET_BRG: `RESET_BRG_VCBUS_DEC=17`,
`RESET_BRG_VDEC_PIPL0=160`, `RESET_BRG_HEVCF_PIPL0=161`, `RESET_BRG_HCODEC_PIPL0=163`; RESET_I2C:
`RESET_I2C_S_A=144`, `RESET_I2C_M_A=145`, `RESET_I2C_M_B=146`, `RESET_I2C_M_C=147`; RESET_PWM:
`RESET_PWM_AB=132`, `RESET_PWM_CD=133`, `RESET_PWM_EF=134`, `RESET_PWM_GH=135`; RESET_UART:
`RESET_UART_A=138`, `RESET_UART_B=139`, `RESET_UART_C=140`, `RESET_UART_D=141`; RESET_USB:
`RESET_USB_DDR0=0`, `RESET_USB_DDR1=1`, `RESET_USB_DDR2=2`, `RESET_USB_DDR3=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_USB_DDR0`,
`RESET_USB_DDR1`, `RESET_USB_DDR2`, `RESET_USB_DDR3`, `RESET_USBCTRL`, `RESET_USBPHY20`,
`RESET_USBPHY21`, `RESET_HDMITX_APB`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-s4-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson8b-clkc-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson8b-clkc-reset.h

Purpose: `amlogic,meson8b-clkc-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 16 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are CLKC (16). Representative constants are
`CLKC_RESET_L2_CACHE_SOFT_RESET`, `CLKC_RESET_AXI_64_TO_128_BRIDGE_A5_SOFT_RESET`,
`CLKC_RESET_SCU_SOFT_RESET`, `CLKC_RESET_CPU0_SOFT_RESET`, `CLKC_RESET_CPU1_SOFT_RESET`,
`CLKC_RESET_CPU2_SOFT_RESET`, `CLKC_RESET_CPU3_SOFT_RESET`, `CLKC_RESET_A5_GLOBAL_RESET`,
`CLKC_RESET_A5_AXI_SOFT_RESET`, `CLKC_RESET_A5_ABP_SOFT_RESET`,
`CLKC_RESET_AXI_64_TO_128_BRIDGE_MMC_SOFT_RESET`, `CLKC_RESET_VID_CLK_CNTL_SOFT_RESET`,
`CLKC_RESET_VID_DIVIDER_CNTL_SOFT_RESET_POST`, `CLKC_RESET_VID_DIVIDER_CNTL_SOFT_RESET_PRE`,
`CLKC_RESET_VID_DIVIDER_CNTL_RESET_N_POST`, `CLKC_RESET_VID_DIVIDER_CNTL_RESET_N_PRE`. Function-like
helpers are none. Value shape: literal numeric range 0..15 across 16 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON8B_CLKC_RESET_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `CLKC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 27 lines long. Notable source comments include
`_DT_BINDINGS_AMLOGIC_MESON8B_CLKC_RESET_H`. Example value clusters are CLKC:
`CLKC_RESET_L2_CACHE_SOFT_RESET=0`, `CLKC_RESET_AXI_64_TO_128_BRIDGE_A5_SOFT_RESET=1`,
`CLKC_RESET_SCU_SOFT_RESET=2`, `CLKC_RESET_CPU0_SOFT_RESET=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`CLKC_RESET_L2_CACHE_SOFT_RESET`, `CLKC_RESET_AXI_64_TO_128_BRIDGE_A5_SOFT_RESET`,
`CLKC_RESET_SCU_SOFT_RESET`, `CLKC_RESET_CPU0_SOFT_RESET`, `CLKC_RESET_CPU1_SOFT_RESET`,
`CLKC_RESET_CPU2_SOFT_RESET`, `CLKC_RESET_CPU3_SOFT_RESET`, `CLKC_RESET_A5_GLOBAL_RESET`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson8b-clkc-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson8b-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson8b-reset.h

Purpose: `amlogic,meson8b-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 98 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_PERIPHS (16), RESET_DEMUX (8), RESET_AHB (5),
RESET_PARSER (5), RESET_AUDIO (4), RESET_SYS (4), RESET_A5 (4), RESET_VLD (2), RESET_DDR (2),
RESET_VDAC (2). Representative constants are `RESET_HIU`, `RESET_VLD`, `RESET_IQIDCT`, `RESET_MC`,
`RESET_VIU`, `RESET_AIU`, `RESET_MCPU`, `RESET_CCPU`, `...`, `RESET_PERIPHS_SDIO`,
`RESET_PERIPHS_UART_0`, `RESET_PERIPHS_UART_1`, `RESET_PERIPHS_ASYNC_0`, `RESET_PERIPHS_ASYNC_1`,
`RESET_PERIPHS_SPI_0`, `RESET_PERIPHS_SPI_1`, `RESET_PERIPHS_LED_PWM`. Function-like helpers are
none. Value shape: literal numeric range 0..207 across 98 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON8B_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET0`, `16-31`, `RESET1`, `48-63`, `RESET2`, `80-95`, `RESET3`, `112-127`, `RESET4`,
`142-159`, `RESET5`, `166-191`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 126 lines long. Notable source comments include `RESET0`, `8`, `16-31`, `RESET1`, `32`,
`48-63`. Example value clusters are RESET_PERIPHS: `RESET_PERIPHS_GENERAL=192`,
`RESET_PERIPHS_IR_REMOTE=193`, `RESET_PERIPHS_SMART_CARD=194`, `RESET_PERIPHS_SAR_ADC=195`;
RESET_DEMUX: `RESET_DEMUX=33`, `RESET_DEMUX_TOP=105`, `RESET_DEMUX_DES=106`,
`RESET_DEMUX_S2P_0=107`; RESET_AHB: `RESET_AHB_SRAM=38`, `RESET_AHB_BRIDGE=39`, `RESET_AHB_DATA=45`,
`RESET_AHB_CNTL=46`; RESET_PARSER: `RESET_PARSER=40`, `RESET_PARSER_REG=71`,
`RESET_PARSER_FETCH=72`, `RESET_PARSER_CTL=73`; RESET_AUDIO: `RESET_AUDIO_APB=76`,
`RESET_AUDIO_PLL_MODULATOR=101`, `RESET_AUDIO_DAC=104`, `RESET_AUDIO_PLL=164`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_HIU`,
`RESET_VLD`, `RESET_IQIDCT`, `RESET_MC`, `RESET_VIU`, `RESET_AIU`, `RESET_MCPU`, `RESET_CCPU`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson8b-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/aspeed,ast2700-scu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/aspeed,ast2700-scu.h

Purpose: `aspeed,ast2700-scu.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 109 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are SCU1 (64), SCU0 (45). Representative constants are
`SCU0_RESET_SDRAM`, `SCU0_RESET_DDRPHY`, `SCU0_RESET_RSA`, `SCU0_RESET_SHA3`, `SCU0_RESET_HACE`,
`SCU0_RESET_SOC`, `SCU0_RESET_VIDEO`, `SCU0_RESET_2D`, `...`, `SCU1_RESET_UHCI`,
`SCU1_RESET_PORTC_USB2UART`, `SCU1_RESET_PORTC_VHUB_EHCI`, `SCU1_RESET_PORTD_USB2UART`,
`SCU1_RESET_PORTD_VHUB_EHCI`, `SCU1_RESET_H2X`, `SCU1_RESET_I3CDMA`, `SCU1_RESET_PCIE2RST`.
Function-like helpers are none. Value shape: literal numeric range 0..63 across 109 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_MACH_ASPEED_AST2700_RESET_H_`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`SOC0`, `SOC1`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 124 lines long. Notable source comments include `Device Tree binding constants for
AST2700 reset controller.`, `SOC0`, `SOC1`, `_MACH_ASPEED_AST2700_RESET_H_`. Example value clusters
are SCU1: `SCU1_RESET_LPC0=0`, `SCU1_RESET_LPC1=1`, `SCU1_RESET_MII=2`, `SCU1_RESET_PECI=3`; SCU0:
`SCU0_RESET_SDRAM=0`, `SCU0_RESET_DDRPHY=1`, `SCU0_RESET_RSA=2`, `SCU0_RESET_SHA3=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `SCU0_RESET_SDRAM`,
`SCU0_RESET_DDRPHY`, `SCU0_RESET_RSA`, `SCU0_RESET_SHA3`, `SCU0_RESET_HACE`, `SCU0_RESET_SOC`,
`SCU0_RESET_VIDEO`, `SCU0_RESET_2D`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/aspeed,ast2700-scu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/axg-aoclkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/axg-aoclkc.h

Purpose: `axg-aoclkc.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_AO (6). Representative constants are
`RESET_AO_REMOTE`, `RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`, `RESET_AO_UART1`, `RESET_AO_UART2`,
`RESET_AO_IR_BLASTER`, `RESET_AO_REMOTE`, `RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`,
`RESET_AO_UART1`, `RESET_AO_UART2`, `RESET_AO_IR_BLASTER`. Function-like helpers are none. Value
shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_RESET_AMLOGIC_MESON_AXG_AOCLK`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RESET_AO group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 20 lines long. Notable source comments include none. Example value clusters are
RESET_AO: `RESET_AO_REMOTE=0`, `RESET_AO_I2C_MASTER=1`, `RESET_AO_I2C_SLAVE=2`, `RESET_AO_UART1=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AO_REMOTE`,
`RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`, `RESET_AO_UART1`, `RESET_AO_UART2`,
`RESET_AO_IR_BLASTER`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/axg-aoclkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm63268-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm63268-reset.h

Purpose: `bcm63268-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 22 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are BCM63268 (22). Representative constants are
`BCM63268_RST_SPI`, `BCM63268_RST_IPSEC`, `BCM63268_RST_EPHY`, `BCM63268_RST_SAR`,
`BCM63268_RST_ENETSW`, `BCM63268_RST_USBS`, `BCM63268_RST_USBH`, `BCM63268_RST_PCM`, `...`,
`BCM63268_RST_WLAN_UBUS`, `BCM63268_RST_DECT`, `BCM63268_RST_FAP1`, `BCM63268_RST_PCIE_HARD`,
`BCM63268_RST_GPHY`, `BCM63268_TRST_SW`, `BCM63268_TRST_HW`, `BCM63268_TRST_POR`. Function-like
helpers are none. Value shape: literal numeric range 0..31 across 22 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_BCM63268_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`BCM63268 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 30 lines long. Notable source comments include `__DT_BINDINGS_RESET_BCM63268_H`. Example
value clusters are BCM63268: `BCM63268_RST_SPI=0`, `BCM63268_RST_IPSEC=1`, `BCM63268_RST_EPHY=2`,
`BCM63268_RST_SAR=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `BCM63268_RST_SPI`,
`BCM63268_RST_IPSEC`, `BCM63268_RST_EPHY`, `BCM63268_RST_SAR`, `BCM63268_RST_ENETSW`,
`BCM63268_RST_USBS`, `BCM63268_RST_USBH`, `BCM63268_RST_PCM`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm63268-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6328-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6328-reset.h

Purpose: `bcm6328-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 11 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are BCM6328 (11). Representative constants are
`BCM6328_RST_SPI`, `BCM6328_RST_EPHY`, `BCM6328_RST_SAR`, `BCM6328_RST_ENETSW`, `BCM6328_RST_USBS`,
`BCM6328_RST_USBH`, `BCM6328_RST_PCM`, `BCM6328_RST_PCIE_CORE`, `BCM6328_RST_ENETSW`,
`BCM6328_RST_USBS`, `BCM6328_RST_USBH`, `BCM6328_RST_PCM`, `BCM6328_RST_PCIE_CORE`,
`BCM6328_RST_PCIE`, `BCM6328_RST_PCIE_EXT`, `BCM6328_RST_PCIE_HARD`. Function-like helpers are none.
Value shape: literal numeric range 0..10 across 11 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_BCM6328_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`BCM6328 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 18 lines long. Notable source comments include `__DT_BINDINGS_RESET_BCM6328_H`. Example
value clusters are BCM6328: `BCM6328_RST_SPI=0`, `BCM6328_RST_EPHY=1`, `BCM6328_RST_SAR=2`,
`BCM6328_RST_ENETSW=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `BCM6328_RST_SPI`,
`BCM6328_RST_EPHY`, `BCM6328_RST_SAR`, `BCM6328_RST_ENETSW`, `BCM6328_RST_USBS`, `BCM6328_RST_USBH`,
`BCM6328_RST_PCM`, `BCM6328_RST_PCIE_CORE`. Test signals include DTS compile checks, reset-
controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6328-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6358-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6358-reset.h

Purpose: `bcm6358-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 8 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are BCM6358 (8). Representative constants are
`BCM6358_RST_SPI`, `BCM6358_RST_ENET`, `BCM6358_RST_MPI`, `BCM6358_RST_EPHY`, `BCM6358_RST_SAR`,
`BCM6358_RST_USBH`, `BCM6358_RST_PCM`, `BCM6358_RST_ADSL`, `BCM6358_RST_SPI`, `BCM6358_RST_ENET`,
`BCM6358_RST_MPI`, `BCM6358_RST_EPHY`, `BCM6358_RST_SAR`, `BCM6358_RST_USBH`, `BCM6358_RST_PCM`,
`BCM6358_RST_ADSL`. Function-like helpers are none. Value shape: literal numeric range 0..14 across
8 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_BCM6358_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`BCM6358 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 15 lines long. Notable source comments include `__DT_BINDINGS_RESET_BCM6358_H`. Example
value clusters are BCM6358: `BCM6358_RST_SPI=0`, `BCM6358_RST_ENET=2`, `BCM6358_RST_MPI=3`,
`BCM6358_RST_EPHY=6`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `BCM6358_RST_SPI`,
`BCM6358_RST_ENET`, `BCM6358_RST_MPI`, `BCM6358_RST_EPHY`, `BCM6358_RST_SAR`, `BCM6358_RST_USBH`,
`BCM6358_RST_PCM`, `BCM6358_RST_ADSL`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6358-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6362-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6362-reset.h

Purpose: `bcm6362-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 15 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are BCM6362 (15). Representative constants are
`BCM6362_RST_SPI`, `BCM6362_RST_IPSEC`, `BCM6362_RST_EPHY`, `BCM6362_RST_SAR`, `BCM6362_RST_ENETSW`,
`BCM6362_RST_USBD`, `BCM6362_RST_USBH`, `BCM6362_RST_PCM`, `BCM6362_RST_PCM`,
`BCM6362_RST_PCIE_CORE`, `BCM6362_RST_PCIE`, `BCM6362_RST_PCIE_EXT`, `BCM6362_RST_WLAN_SHIM`,
`BCM6362_RST_DDR_PHY`, `BCM6362_RST_FAP`, `BCM6362_RST_WLAN_UBUS`. Function-like helpers are none.
Value shape: literal numeric range 0..14 across 15 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_BCM6362_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`BCM6362 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 22 lines long. Notable source comments include `__DT_BINDINGS_RESET_BCM6362_H`. Example
value clusters are BCM6362: `BCM6362_RST_SPI=0`, `BCM6362_RST_IPSEC=1`, `BCM6362_RST_EPHY=2`,
`BCM6362_RST_SAR=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `BCM6362_RST_SPI`,
`BCM6362_RST_IPSEC`, `BCM6362_RST_EPHY`, `BCM6362_RST_SAR`, `BCM6362_RST_ENETSW`,
`BCM6362_RST_USBD`, `BCM6362_RST_USBH`, `BCM6362_RST_PCM`. Test signals include DTS compile checks,
reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6362-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6368-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6368-reset.h

Purpose: `bcm6368-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are BCM6368 (9). Representative constants are
`BCM6368_RST_SPI`, `BCM6368_RST_MPI`, `BCM6368_RST_IPSEC`, `BCM6368_RST_EPHY`, `BCM6368_RST_SAR`,
`BCM6368_RST_SWITCH`, `BCM6368_RST_USBD`, `BCM6368_RST_USBH`, `BCM6368_RST_MPI`,
`BCM6368_RST_IPSEC`, `BCM6368_RST_EPHY`, `BCM6368_RST_SAR`, `BCM6368_RST_SWITCH`,
`BCM6368_RST_USBD`, `BCM6368_RST_USBH`, `BCM6368_RST_PCM`. Function-like helpers are none. Value
shape: literal numeric range 0..13 across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_BCM6368_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`BCM6368 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 16 lines long. Notable source comments include `__DT_BINDINGS_RESET_BCM6368_H`. Example
value clusters are BCM6368: `BCM6368_RST_SPI=0`, `BCM6368_RST_MPI=3`, `BCM6368_RST_IPSEC=4`,
`BCM6368_RST_EPHY=6`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `BCM6368_RST_SPI`,
`BCM6368_RST_MPI`, `BCM6368_RST_IPSEC`, `BCM6368_RST_EPHY`, `BCM6368_RST_SAR`, `BCM6368_RST_SWITCH`,
`BCM6368_RST_USBD`, `BCM6368_RST_USBH`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6368-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bitmain,bm1880-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bitmain,bm1880-reset.h

Purpose: `bitmain,bm1880-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 40 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are BM1880 (40). Representative constants are
`BM1880_RST_MAIN_AP`, `BM1880_RST_SECOND_AP`, `BM1880_RST_DDR`, `BM1880_RST_VIDEO`,
`BM1880_RST_JPEG`, `BM1880_RST_VPP`, `BM1880_RST_GDMA`, `BM1880_RST_AXI_SRAM`, `...`,
`BM1880_RST_SPI`, `BM1880_RST_GPIO0`, `BM1880_RST_GPIO1`, `BM1880_RST_GPIO2`, `BM1880_RST_EFUSE`,
`BM1880_RST_WDT`, `BM1880_RST_AHB_ROM`, `BM1880_RST_SPIC`. Function-like helpers are none. Value
shape: literal numeric range 0..39 across 40 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_BM1880_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`BM1880 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 51 lines long. Notable source comments include `_DT_BINDINGS_BM1880_RESET_H`. Example
value clusters are BM1880: `BM1880_RST_MAIN_AP=0`, `BM1880_RST_SECOND_AP=1`, `BM1880_RST_DDR=2`,
`BM1880_RST_VIDEO=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `BM1880_RST_MAIN_AP`,
`BM1880_RST_SECOND_AP`, `BM1880_RST_DDR`, `BM1880_RST_VIDEO`, `BM1880_RST_JPEG`, `BM1880_RST_VPP`,
`BM1880_RST_GDMA`, `BM1880_RST_AXI_SRAM`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bitmain,bm1880-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bt1-ccu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bt1-ccu.h

Purpose: `bt1-ccu.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 22 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are CCU_AXI (11), CCU_SYS (11). Representative constants
are `CCU_AXI_MAIN_RST`, `CCU_AXI_DDR_RST`, `CCU_AXI_SATA_RST`, `CCU_AXI_GMAC0_RST`,
`CCU_AXI_GMAC1_RST`, `CCU_AXI_XGMAC_RST`, `CCU_AXI_PCIE_M_RST`, `CCU_AXI_PCIE_S_RST`, `...`,
`CCU_SYS_DDR_INIT_RST`, `CCU_SYS_PCIE_PCS_PHY_RST`, `CCU_SYS_PCIE_PIPE0_RST`,
`CCU_SYS_PCIE_CORE_RST`, `CCU_SYS_PCIE_PWR_RST`, `CCU_SYS_PCIE_STICKY_RST`,
`CCU_SYS_PCIE_NSTICKY_RST`, `CCU_SYS_PCIE_HOT_RST`. Function-like helpers are none. Value shape:
literal numeric range 0..10 across 22 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_BT1_CCU_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`CCU_AXI group`, `CCU_SYS group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 34 lines long. Notable source comments include `Baikal-T1 CCU reset indices`,
`__DT_BINDINGS_RESET_BT1_CCU_H`. Example value clusters are CCU_AXI: `CCU_AXI_MAIN_RST=0`,
`CCU_AXI_DDR_RST=1`, `CCU_AXI_SATA_RST=2`, `CCU_AXI_GMAC0_RST=3`; CCU_SYS: `CCU_SYS_SATA_REF_RST=0`,
`CCU_SYS_APB_RST=1`, `CCU_SYS_DDR_FULL_RST=2`, `CCU_SYS_DDR_INIT_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CCU_AXI_MAIN_RST`,
`CCU_AXI_DDR_RST`, `CCU_AXI_SATA_RST`, `CCU_AXI_GMAC0_RST`, `CCU_AXI_GMAC1_RST`,
`CCU_AXI_XGMAC_RST`, `CCU_AXI_PCIE_M_RST`, `CCU_AXI_PCIE_S_RST`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/bt1-ccu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/canaan,k230-rst.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/canaan,k230-rst.h

Purpose: `canaan,k230-rst.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 80 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RST_SHRM (3), RST_ISP (3), RST_CPU0 (2), RST_CPU1
(2), RST_HISYS (2), RST_USB0 (2), RST_USB1 (2), RST_WDT0 (2), RST_WDT1 (2), RST_GPIO (2).
Representative constants are `RST_CPU0`, `RST_CPU1`, `RST_CPU0_FLUSH`, `RST_CPU1_FLUSH`, `RST_AI`,
`RST_VPU`, `RST_HISYS`, `RST_HISYS_AHB`, `...`, `RST_CSI1`, `RST_CSI2`, `RST_CSI_DPHY`,
`RST_ISP_AHB`, `RST_M0`, `RST_M1`, `RST_M2`, `RST_SPI2AXI`. Function-like helpers are none. Value
shape: literal numeric range 0..79 across 80 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_CANAAN_K230_RST_H_`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`RST_SHRM group`, `RST_ISP group`, `RST_CPU0 group`, `RST_CPU1 group`, `RST_HISYS group`, `RST_USB0
group`, `RST_USB1 group`, `RST_WDT0 group`, `RST_WDT1 group`, `RST_GPIO group`, `RST_ADC group`,
`RST_AI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 90 lines long. Notable source comments include none. Example value clusters are
RST_SHRM: `RST_SHRM_AXIM=23`, `RST_SHRM_AXIS=24`, `RST_SHRM_APB=70`; RST_ISP: `RST_ISP=27`,
`RST_ISP_DW=28`, `RST_ISP_AHB=75`; RST_CPU0: `RST_CPU0=0`, `RST_CPU0_FLUSH=2`; RST_CPU1:
`RST_CPU1=1`, `RST_CPU1_FLUSH=3`; RST_HISYS: `RST_HISYS=6`, `RST_HISYS_AHB=7`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RST_CPU0`, `RST_CPU1`,
`RST_CPU0_FLUSH`, `RST_CPU1_FLUSH`, `RST_AI`, `RST_VPU`, `RST_HISYS`, `RST_HISYS_AHB`. Test signals
include DTS compile checks, reset-controller probe, driver reset/deassert paths, and peripheral
reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/canaan,k230-rst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/cix,sky1-s5-system-control.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/cix,sky1-s5-system-control.h

Purpose: `cix,sky1-s5-system-control.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 143 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are SKY1 (143). Representative constants are
`SKY1_CSU_PM_RESET_N`, `SKY1_SENSORFUSION_RESET_N`, `SKY1_SENSORFUSION_NOC_RESET_N`,
`SKY1_DDRC_RESET_N`, `SKY1_GIC_RESET_N`, `SKY1_CI700_RESET_N`, `SKY1_SYS_NI700_RESET_N`,
`SKY1_MM_NI700_RESET_N`, `...`, `SKY1_RCSU_USB2_HOST2_RESET_N`, `SKY1_RCSU_USB2_HOST3_RESET_N`,
`SKY1_RCSU_USB3_TYPEA_DRD_RESET_N`, `SKY1_RCSU_USB3_TYPEC_DRD_RESET_N`,
`SKY1_RCSU_USB3_TYPEC_HOST0_RESET_N`, `SKY1_RCSU_USB3_TYPEC_HOST1_RESET_N`,
`SKY1_RCSU_USB3_TYPEC_HOST2_RESET_N`, `SKY1_VPU_RCSU_RESET_N`. Function-like helpers are none. Value
shape: literal numeric range 0..142 across 143 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_CIX_SKY1_S5_SYSTEM_CONTROL_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `reset for csu_pm`, `reset group0 for s0 domain modules`, `reset group1 for s0 domain
modules`, `reset group1 for usb phys`, `reset group1 for usb controllers`, `reset group0 for rcsu`,
`reset group1 for rcsu`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 163 lines long. Notable source comments include `reset for csu_pm`, `reset group0 for s0
domain modules`, `reset group1 for s0 domain modules`, `reset group1 for usb phys`, `reset group1
for usb controllers`, `reset group0 for rcsu`. Example value clusters are SKY1:
`SKY1_CSU_PM_RESET_N=0`, `SKY1_SENSORFUSION_RESET_N=1`, `SKY1_SENSORFUSION_NOC_RESET_N=2`,
`SKY1_DDRC_RESET_N=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `SKY1_CSU_PM_RESET_N`,
`SKY1_SENSORFUSION_RESET_N`, `SKY1_SENSORFUSION_NOC_RESET_N`, `SKY1_DDRC_RESET_N`,
`SKY1_GIC_RESET_N`, `SKY1_CI700_RESET_N`, `SKY1_SYS_NI700_RESET_N`, `SKY1_MM_NI700_RESET_N`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/cix,sky1-s5-system-control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/cix,sky1-system-control.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/cix,sky1-system-control.h

Purpose: `cix,sky1-system-control.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 29 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are SW_I3C0 (3), SW_I3C1 (3), SW_UART0 (2), SW_UART1
(2), SW_UART2 (2), SW_UART3 (2), SW_XSPI (2), SW_TIMER (1), SW_DMA (1), SW_SPI0 (1). Representative
constants are `SW_I3C0_RST_FUNC_G_N`, `SW_I3C0_RST_FUNC_I_N`, `SW_I3C1_RST_FUNC_G_N`,
`SW_I3C1_RST_FUNC_I_N`, `SW_UART0_RST_FUNC_N`, `SW_UART1_RST_FUNC_N`, `SW_UART2_RST_FUNC_N`,
`SW_UART3_RST_FUNC_N`, `...`, `SW_I2C3_RST_APB_N`, `SW_I2C4_RST_APB_N`, `SW_I2C5_RST_APB_N`,
`SW_I2C6_RST_APB_N`, `SW_I2C7_RST_APB_N`, `SW_GPIO_RST_APB_N`, `SW_XSPI_REG_RST_N`,
`SW_XSPI_SYS_RST_N`. Function-like helpers are none. Value shape: literal numeric range 0..28 across
29 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_CIX_SKY1_SYSTEM_CONTROL_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `func reset for sky1 fch`, `apb reset for sky1 fch`, `fch rst for xspi`, which is the
intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 41 lines long. Notable source comments include `func reset for sky1 fch`, `apb reset for
sky1 fch`, `fch rst for xspi`. Example value clusters are SW_I3C0: `SW_I3C0_RST_FUNC_G_N=0`,
`SW_I3C0_RST_FUNC_I_N=1`, `SW_I3C0_RST_APB_N=9`; SW_I3C1: `SW_I3C1_RST_FUNC_G_N=2`,
`SW_I3C1_RST_FUNC_I_N=3`, `SW_I3C1_RST_APB_N=10`; SW_UART0: `SW_UART0_RST_FUNC_N=4`,
`SW_UART0_RST_APB_N=12`; SW_UART1: `SW_UART1_RST_FUNC_N=5`, `SW_UART1_RST_APB_N=13`; SW_UART2:
`SW_UART2_RST_FUNC_N=6`, `SW_UART2_RST_APB_N=14`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `SW_I3C0_RST_FUNC_G_N`,
`SW_I3C0_RST_FUNC_I_N`, `SW_I3C1_RST_FUNC_G_N`, `SW_I3C1_RST_FUNC_I_N`, `SW_UART0_RST_FUNC_N`,
`SW_UART1_RST_FUNC_N`, `SW_UART2_RST_FUNC_N`, `SW_UART3_RST_FUNC_N`. Test signals include DTS
compile checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization
after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/cix,sky1-system-control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/cortina,gemini-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/cortina,gemini-reset.h

Purpose: `cortina,gemini-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 31 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are GEMINI (31). Representative constants are
`GEMINI_RESET_DRAM`, `GEMINI_RESET_FLASH`, `GEMINI_RESET_IDE`, `GEMINI_RESET_RAID`,
`GEMINI_RESET_SECURITY`, `GEMINI_RESET_GMAC0`, `GEMINI_RESET_GMAC1`, `GEMINI_RESET_PCI`, `...`,
`GEMINI_RESET_WDOG`, `GEMINI_RESET_EXTERN`, `GEMINI_RESET_CIR`, `GEMINI_RESET_SATA0`,
`GEMINI_RESET_SATA1`, `GEMINI_RESET_TVC`, `GEMINI_RESET_CPU1`, `GEMINI_RESET_GLOBAL`. Function-like
helpers are none. Value shape: literal numeric range 0..31 across 31 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CORTINA_GEMINI_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `GEMINI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 37 lines long. Notable source comments include none. Example value clusters are GEMINI:
`GEMINI_RESET_DRAM=0`, `GEMINI_RESET_FLASH=1`, `GEMINI_RESET_IDE=2`, `GEMINI_RESET_RAID=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `GEMINI_RESET_DRAM`,
`GEMINI_RESET_FLASH`, `GEMINI_RESET_IDE`, `GEMINI_RESET_RAID`, `GEMINI_RESET_SECURITY`,
`GEMINI_RESET_GMAC0`, `GEMINI_RESET_GMAC1`, `GEMINI_RESET_PCI`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/cortina,gemini-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/delta,tn48m-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/delta,tn48m-reset.h

Purpose: `delta,tn48m-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are CPU_88F7040 (1), CPU_88F6820 (1), MAC_98DX3265 (1),
PHY_88E1680 (1), PHY_88E1512 (1), POE_RESET (1). Representative constants are `CPU_88F7040_RESET`,
`CPU_88F6820_RESET`, `MAC_98DX3265_RESET`, `PHY_88E1680_RESET`, `PHY_88E1512_RESET`, `POE_RESET`,
`CPU_88F7040_RESET`, `CPU_88F6820_RESET`, `MAC_98DX3265_RESET`, `PHY_88E1680_RESET`,
`PHY_88E1512_RESET`, `POE_RESET`. Function-like helpers are none. Value shape: literal numeric range
0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_TN48M_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`CPU_88F7040 group`, `CPU_88F6820 group`, `MAC_98DX3265 group`, `PHY_88E1680 group`, `PHY_88E1512
group`, `POE_RESET group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 20 lines long. Notable source comments include `Delta TN48M CPLD GPIO driver`,
`_DT_BINDINGS_RESET_TN48M_H`. Example value clusters are CPU_88F7040: `CPU_88F7040_RESET=0`;
CPU_88F6820: `CPU_88F6820_RESET=1`; MAC_98DX3265: `MAC_98DX3265_RESET=2`; PHY_88E1680:
`PHY_88E1680_RESET=3`; PHY_88E1512: `PHY_88E1512_RESET=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CPU_88F7040_RESET`,
`CPU_88F6820_RESET`, `MAC_98DX3265_RESET`, `PHY_88E1680_RESET`, `PHY_88E1512_RESET`, `POE_RESET`.
Test signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/delta,tn48m-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/econet,en751221-scu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/econet,en751221-scu.h

Purpose: `econet,en751221-scu.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 42 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EN751221 (42). Representative constants are
`EN751221_XPON_PHY_RST`, `EN751221_PCM1_ZSI_ISI_RST`, `EN751221_FE_QDMA1_RST`,
`EN751221_FE_QDMA2_RST`, `EN751221_FE_UNZIP_RST`, `EN751221_PCM2_RST`, `EN751221_PTM_MAC_RST`,
`EN751221_CRYPTO_RST`, `...`, `EN751221_UART4_RST`, `EN751221_UART5_RST`, `EN751221_I2C2_RST`,
`EN751221_XSI_MAC_RST`, `EN751221_XSI_PHY_RST`, `EN751221_DMT_RST`, `EN751221_USB_PHY_P0_RST`,
`EN751221_USB_PHY_P1_RST`. Function-like helpers are none. Value shape: literal numeric range 0..41
across 42 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_CONTROLLER_ECONET_EN751221_H_`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `EN751221 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 49 lines long. Notable source comments include
`__DT_BINDINGS_RESET_CONTROLLER_ECONET_EN751221_H_`. Example value clusters are EN751221:
`EN751221_XPON_PHY_RST=0`, `EN751221_PCM1_ZSI_ISI_RST=1`, `EN751221_FE_QDMA1_RST=2`,
`EN751221_FE_QDMA2_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`EN751221_XPON_PHY_RST`, `EN751221_PCM1_ZSI_ISI_RST`, `EN751221_FE_QDMA1_RST`,
`EN751221_FE_QDMA2_RST`, `EN751221_FE_UNZIP_RST`, `EN751221_PCM2_RST`, `EN751221_PTM_MAC_RST`,
`EN751221_CRYPTO_RST`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/econet,en751221-scu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/eswin,eic7700-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/eswin,eic7700-reset.h

Purpose: `eswin,eic7700-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 281 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EIC7700 (281). Representative constants are
`EIC7700_RESET_NOC_NSP`, `EIC7700_RESET_NOC_CFG`, `EIC7700_RESET_RNOC_NSP`,
`EIC7700_RESET_SNOC_TCU`, `EIC7700_RESET_SNOC_U84`, `EIC7700_RESET_SNOC_PCIE_XSR`,
`EIC7700_RESET_SNOC_PCIE_XMR`, `EIC7700_RESET_SNOC_PCIE_PR`, `...`, `EIC7700_RESET_CNOC_D2D_CFG`,
`EIC7700_RESET_CNOC_CFG`, `EIC7700_RESET_CNOC_CLMM_CFG`, `EIC7700_RESET_CNOC_AON_CFG`,
`EIC7700_RESET_LNOC_CFG`, `EIC7700_RESET_LNOC_NPU_LLC`, `EIC7700_RESET_LNOC_DDRC1_P0`,
`EIC7700_RESET_LNOC_DDRC0_P0`. Function-like helpers are none. Value shape: literal numeric range
0..280 across 281 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_ESWIN_EIC7700_RESET_H__`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`EIC7700 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 298 lines long. Notable source comments include `All rights reserved. Device Tree
binding constants for EIC7700 reset controller. Authors: Yifeng Huang
<huangyifeng@eswincomputing.com> Xuyang Dong <dongxuyang@eswincomputing.com>`,
`__DT_ESWIN_EIC7700_RESET_H__`. Example value clusters are EIC7700: `EIC7700_RESET_NOC_NSP=0`,
`EIC7700_RESET_NOC_CFG=1`, `EIC7700_RESET_RNOC_NSP=2`, `EIC7700_RESET_SNOC_TCU=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`EIC7700_RESET_NOC_NSP`, `EIC7700_RESET_NOC_CFG`, `EIC7700_RESET_RNOC_NSP`,
`EIC7700_RESET_SNOC_TCU`, `EIC7700_RESET_SNOC_U84`, `EIC7700_RESET_SNOC_PCIE_XSR`,
`EIC7700_RESET_SNOC_PCIE_XMR`, `EIC7700_RESET_SNOC_PCIE_PR`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/eswin,eic7700-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/fsl,imx8ulp-sim-lpav.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/fsl,imx8ulp-sim-lpav.h

Purpose: `fsl,imx8ulp-sim-lpav.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are IMX8ULP (6). Representative constants are
`IMX8ULP_SIM_LPAV_HIFI4_DSP_DBG_RST`, `IMX8ULP_SIM_LPAV_HIFI4_DSP_RST`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_STALL`, `IMX8ULP_SIM_LPAV_DSI_RST_BYTE_N`,
`IMX8ULP_SIM_LPAV_DSI_RST_ESC_N`, `IMX8ULP_SIM_LPAV_DSI_RST_DPI_N`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_DBG_RST`, `IMX8ULP_SIM_LPAV_HIFI4_DSP_RST`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_STALL`, `IMX8ULP_SIM_LPAV_DSI_RST_BYTE_N`,
`IMX8ULP_SIM_LPAV_DSI_RST_ESC_N`, `IMX8ULP_SIM_LPAV_DSI_RST_DPI_N`. Function-like helpers are none.
Value shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_IMX8ULP_SIM_LPAV_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `IMX8ULP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 16 lines long. Notable source comments include `DT_BINDING_RESET_IMX8ULP_SIM_LPAV_H`.
Example value clusters are IMX8ULP: `IMX8ULP_SIM_LPAV_HIFI4_DSP_DBG_RST=0`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_RST=1`, `IMX8ULP_SIM_LPAV_HIFI4_DSP_STALL=2`,
`IMX8ULP_SIM_LPAV_DSI_RST_BYTE_N=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`IMX8ULP_SIM_LPAV_HIFI4_DSP_DBG_RST`, `IMX8ULP_SIM_LPAV_HIFI4_DSP_RST`,
`IMX8ULP_SIM_LPAV_HIFI4_DSP_STALL`, `IMX8ULP_SIM_LPAV_DSI_RST_BYTE_N`,
`IMX8ULP_SIM_LPAV_DSI_RST_ESC_N`, `IMX8ULP_SIM_LPAV_DSI_RST_DPI_N`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/fsl,imx8ulp-sim-lpav.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/g12a-aoclkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/g12a-aoclkc.h

Purpose: `g12a-aoclkc.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_AO (7). Representative constants are
`RESET_AO_IR_IN`, `RESET_AO_UART`, `RESET_AO_I2C_M`, `RESET_AO_I2C_S`, `RESET_AO_SAR_ADC`,
`RESET_AO_UART2`, `RESET_AO_IR_OUT`, `RESET_AO_IR_IN`, `RESET_AO_UART`, `RESET_AO_I2C_M`,
`RESET_AO_I2C_S`, `RESET_AO_SAR_ADC`, `RESET_AO_UART2`, `RESET_AO_IR_OUT`. Function-like helpers are
none. Value shape: literal numeric range 0..6 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_RESET_AMLOGIC_MESON_G12A_AOCLK`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RESET_AO group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 18 lines long. Notable source comments include none. Example value clusters are
RESET_AO: `RESET_AO_IR_IN=0`, `RESET_AO_UART=1`, `RESET_AO_I2C_M=2`, `RESET_AO_I2C_S=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AO_IR_IN`,
`RESET_AO_UART`, `RESET_AO_I2C_M`, `RESET_AO_I2C_S`, `RESET_AO_SAR_ADC`, `RESET_AO_UART2`,
`RESET_AO_IR_OUT`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/g12a-aoclkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/gxbb-aoclkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/gxbb-aoclkc.h

Purpose: `gxbb-aoclkc.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_AO (6). Representative constants are
`RESET_AO_REMOTE`, `RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`, `RESET_AO_UART1`, `RESET_AO_UART2`,
`RESET_AO_IR_BLASTER`, `RESET_AO_REMOTE`, `RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`,
`RESET_AO_UART1`, `RESET_AO_UART2`, `RESET_AO_IR_BLASTER`. Function-like helpers are none. Value
shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_RESET_AMLOGIC_MESON_GXBB_AOCLK`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RESET_AO group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 66 lines long. Notable source comments include `This file is provided under a dual
BSD/GPLv2 license. When using or redistributing this file, you may do so under either license. GPL
LICENSE SUMMARY This program is free software; you can redistribute it and/or modify it under the
terms of version 2 of the GNU General Public License as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details. You should have received a copy of the GNU General Public
License along with this program; if not, see <http://www.gnu.org/licenses/>. The full GNU General
Public License is included in this distribution in the file called COPYING. BSD LICENSE
Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met: * Redistributions of source code must retain the
above copyright notice, this list of conditions and the following disclaimer. * Redistributions in
binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution. * Neither the
name of Intel Corporation nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission. THIS SOFTWARE IS
PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.`. Example value clusters are RESET_AO:
`RESET_AO_REMOTE=0`, `RESET_AO_I2C_MASTER=1`, `RESET_AO_I2C_SLAVE=2`, `RESET_AO_UART1=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AO_REMOTE`,
`RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`, `RESET_AO_UART1`, `RESET_AO_UART2`,
`RESET_AO_IR_BLASTER`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/gxbb-aoclkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/hisi,hi6220-resets.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/hisi,hi6220-resets.h

Purpose: `hisi,hi6220-resets.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 71 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are PERIPH (58), MEDIA (7), AO_G3D (1), AO_CODECISP (1),
AO_MCPU (1), AO_BBPHARQMEM (1), AO_HIFI (1), AO_ACPUSCUL2C (1). Representative constants are
`PERIPH_RSTDIS0_MMC0`, `PERIPH_RSTDIS0_MMC1`, `PERIPH_RSTDIS0_MMC2`, `PERIPH_RSTDIS0_NANDC`,
`PERIPH_RSTDIS0_USBOTG_BUS`, `PERIPH_RSTDIS0_POR_PICOPHY`, `PERIPH_RSTDIS0_USBOTG`,
`PERIPH_RSTDIS0_USBOTG_32K`, `...`, `MEDIA_MMU`, `MEDIA_XG2RAM1`, `AO_G3D`, `AO_CODECISP`,
`AO_MCPU`, `AO_BBPHARQMEM`, `AO_HIFI`, `AO_ACPUSCUL2C`. Function-like helpers are none. Value shape:
literal numeric range 0..1288 across 71 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_HI6220`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PERIPH group`, `MEDIA group`, `AO_G3D group`, `AO_CODECISP group`, `AO_MCPU group`,
`AO_BBPHARQMEM group`, `AO_HIFI group`, `AO_ACPUSCUL2C group`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 83 lines long. Notable source comments include `This header provides index for the reset
controller based on hi6220 SoC.`, `_DT_BINDINGS_RESET_CONTROLLER_HI6220`. Example value clusters are
PERIPH: `PERIPH_RSTDIS0_MMC0=0x000`, `PERIPH_RSTDIS0_MMC1=0x001`, `PERIPH_RSTDIS0_MMC2=0x002`,
`PERIPH_RSTDIS0_NANDC=0x003`; MEDIA: `MEDIA_G3D=0`, `MEDIA_CODEC_VPU=2`, `MEDIA_CODEC_JPEG=3`,
`MEDIA_ISP=4`; AO_G3D: `AO_G3D=1`; AO_CODECISP: `AO_CODECISP=2`; AO_MCPU: `AO_MCPU=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `PERIPH_RSTDIS0_MMC0`,
`PERIPH_RSTDIS0_MMC1`, `PERIPH_RSTDIS0_MMC2`, `PERIPH_RSTDIS0_NANDC`, `PERIPH_RSTDIS0_USBOTG_BUS`,
`PERIPH_RSTDIS0_POR_PICOPHY`, `PERIPH_RSTDIS0_USBOTG`, `PERIPH_RSTDIS0_USBOTG_32K`. Test signals
include DTS compile checks, reset-controller probe, driver reset/deassert paths, and peripheral
reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/hisi,hi6220-resets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx7-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx7-reset.h

Purpose: `imx7-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 27 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are IMX7 (27). Representative constants are
`IMX7_RESET_A7_CORE_POR_RESET0`, `IMX7_RESET_A7_CORE_POR_RESET1`, `IMX7_RESET_A7_CORE_RESET0`,
`IMX7_RESET_A7_CORE_RESET1`, `IMX7_RESET_A7_DBG_RESET0`, `IMX7_RESET_A7_DBG_RESET1`,
`IMX7_RESET_A7_ETM_RESET0`, `IMX7_RESET_A7_ETM_RESET1`, `...`, `IMX7_RESET_MIPI_PHY_SRST`,
`IMX7_RESET_PCIEPHY`, `IMX7_RESET_PCIEPHY_PERST`, `IMX7_RESET_PCIE_CTRL_APPS_EN`,
`IMX7_RESET_DDRC_PRST`, `IMX7_RESET_DDRC_CORE_RST`, `IMX7_RESET_PCIE_CTRL_APPS_TURNOFF`,
`IMX7_RESET_NUM`. Function-like helpers are none. Value shape: literal numeric range 0..26 across 27
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_IMX7_H`; after preprocessing, DTS C-preprocessor users and C drivers see only the
constants and any packing helpers. Comment-delimited groups or observed macro clusters are `IMX7
group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 53 lines long. Notable source comments include `IMX7_RESET_PCIEPHY is a logical reset
line combining PCIEPHY_BTN and PCIEPHY_G_RST`, `IMX7_RESET_PCIE_CTRL_APPS_EN is not strictly a reset
line, but it can be used to inhibit PCIe LTTSM, so, in a way, it can be thoguht of as one`. Example
value clusters are IMX7: `IMX7_RESET_A7_CORE_POR_RESET0=0`, `IMX7_RESET_A7_CORE_POR_RESET1=1`,
`IMX7_RESET_A7_CORE_RESET0=2`, `IMX7_RESET_A7_CORE_RESET1=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`IMX7_RESET_A7_CORE_POR_RESET0`, `IMX7_RESET_A7_CORE_POR_RESET1`, `IMX7_RESET_A7_CORE_RESET0`,
`IMX7_RESET_A7_CORE_RESET1`, `IMX7_RESET_A7_DBG_RESET0`, `IMX7_RESET_A7_DBG_RESET1`,
`IMX7_RESET_A7_ETM_RESET0`, `IMX7_RESET_A7_ETM_RESET1`. Test signals include DTS compile checks,
reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx7-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mp-reset-audiomix.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mp-reset-audiomix.h

Purpose: `imx8mp-reset-audiomix.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are IMX8MP (3). Representative constants are
`IMX8MP_AUDIOMIX_EARC_RESET`, `IMX8MP_AUDIOMIX_EARC_PHY_RESET`, `IMX8MP_AUDIOMIX_DSP_RUNSTALL`,
`IMX8MP_AUDIOMIX_EARC_RESET`, `IMX8MP_AUDIOMIX_EARC_PHY_RESET`, `IMX8MP_AUDIOMIX_DSP_RUNSTALL`.
Function-like helpers are none. Value shape: literal numeric range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_IMX8MP_AUDIOMIX_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `IMX8MP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 13 lines long. Notable source comments include `DT_BINDING_RESET_IMX8MP_AUDIOMIX_H`.
Example value clusters are IMX8MP: `IMX8MP_AUDIOMIX_EARC_RESET=0`,
`IMX8MP_AUDIOMIX_EARC_PHY_RESET=1`, `IMX8MP_AUDIOMIX_DSP_RUNSTALL=2`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`IMX8MP_AUDIOMIX_EARC_RESET`, `IMX8MP_AUDIOMIX_EARC_PHY_RESET`, `IMX8MP_AUDIOMIX_DSP_RUNSTALL`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mp-reset-audiomix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mp-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mp-reset.h

Purpose: `imx8mp-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 39 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are IMX8MP (39). Representative constants are
`IMX8MP_RESET_A53_CORE_POR_RESET0`, `IMX8MP_RESET_A53_CORE_POR_RESET1`,
`IMX8MP_RESET_A53_CORE_POR_RESET2`, `IMX8MP_RESET_A53_CORE_POR_RESET3`,
`IMX8MP_RESET_A53_CORE_RESET0`, `IMX8MP_RESET_A53_CORE_RESET1`, `IMX8MP_RESET_A53_CORE_RESET2`,
`IMX8MP_RESET_A53_CORE_RESET3`, `...`, `IMX8MP_RESET_GPU3D_RESET`, `IMX8MP_RESET_GPU_RESET`,
`IMX8MP_RESET_VPU_RESET`, `IMX8MP_RESET_VPU_G1_RESET`, `IMX8MP_RESET_VPU_G2_RESET`,
`IMX8MP_RESET_VPUVC8KE_RESET`, `IMX8MP_RESET_NOC_RESET`, `IMX8MP_RESET_NUM`. Function-like helpers
are none. Value shape: literal numeric range 0..38 across 39 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_IMX8MP_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX8MP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 50 lines long. Notable source comments include none. Example value clusters are IMX8MP:
`IMX8MP_RESET_A53_CORE_POR_RESET0=0`, `IMX8MP_RESET_A53_CORE_POR_RESET1=1`,
`IMX8MP_RESET_A53_CORE_POR_RESET2=2`, `IMX8MP_RESET_A53_CORE_POR_RESET3=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`IMX8MP_RESET_A53_CORE_POR_RESET0`, `IMX8MP_RESET_A53_CORE_POR_RESET1`,
`IMX8MP_RESET_A53_CORE_POR_RESET2`, `IMX8MP_RESET_A53_CORE_POR_RESET3`,
`IMX8MP_RESET_A53_CORE_RESET0`, `IMX8MP_RESET_A53_CORE_RESET1`, `IMX8MP_RESET_A53_CORE_RESET2`,
`IMX8MP_RESET_A53_CORE_RESET3`. Test signals include DTS compile checks, reset-controller probe,
driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mp-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mq-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mq-reset.h

Purpose: `imx8mq-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 54 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are IMX8MQ (54). Representative constants are
`IMX8MQ_RESET_A53_CORE_POR_RESET0`, `IMX8MQ_RESET_A53_CORE_POR_RESET1`,
`IMX8MQ_RESET_A53_CORE_POR_RESET2`, `IMX8MQ_RESET_A53_CORE_POR_RESET3`,
`IMX8MQ_RESET_A53_CORE_RESET0`, `IMX8MQ_RESET_A53_CORE_RESET1`, `IMX8MQ_RESET_A53_CORE_RESET2`,
`IMX8MQ_RESET_A53_CORE_RESET3`, `...`, `IMX8MQ_RESET_DDRC1_PHY_RESET`, `IMX8MQ_RESET_DDRC2_PRST`,
`IMX8MQ_RESET_DDRC2_CORE_RESET`, `IMX8MQ_RESET_DDRC2_PHY_RESET`, `IMX8MQ_RESET_SW_M4C_RST`,
`IMX8MQ_RESET_SW_M4P_RST`, `IMX8MQ_RESET_M4_ENABLE`, `IMX8MQ_RESET_NUM`. Function-like helpers are
none. Value shape: literal numeric range 0..53 across 26 macros; 28 alias or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_IMX8MQ_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`IMX8MQ group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 67 lines long. Notable source comments include `i.MX8MN does NOT support`, `i.MX8MN does
NOT support`, `i.MX8MN does NOT support`, `i.MX8MN does NOT support`, `i.MX8MN does NOT support`,
`i.MX8MN does NOT support`. Example value clusters are IMX8MQ: `IMX8MQ_RESET_A53_CORE_POR_RESET0=0`,
`IMX8MQ_RESET_A53_CORE_POR_RESET1=1`, `IMX8MQ_RESET_A53_CORE_POR_RESET2=2`,
`IMX8MQ_RESET_A53_CORE_POR_RESET3=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`IMX8MQ_RESET_A53_CORE_POR_RESET0`, `IMX8MQ_RESET_A53_CORE_POR_RESET1`,
`IMX8MQ_RESET_A53_CORE_POR_RESET2`, `IMX8MQ_RESET_A53_CORE_POR_RESET3`,
`IMX8MQ_RESET_A53_CORE_RESET0`, `IMX8MQ_RESET_A53_CORE_RESET1`, `IMX8MQ_RESET_A53_CORE_RESET2`,
`IMX8MQ_RESET_A53_CORE_RESET3`. Test signals include DTS compile checks, reset-controller probe,
driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx8mq-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/k210-rst.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/k210-rst.h

Purpose: `k210-rst.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 28 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are K210 (28). Representative constants are
`K210_RST_ROM`, `K210_RST_DMA`, `K210_RST_AI`, `K210_RST_DVP`, `K210_RST_FFT`, `K210_RST_GPIO`,
`K210_RST_SPI0`, `K210_RST_SPI1`, `...`, `K210_RST_FPIOA`, `K210_RST_TIMER0`, `K210_RST_TIMER1`,
`K210_RST_TIMER2`, `K210_RST_WDT0`, `K210_RST_WDT1`, `K210_RST_SHA`, `K210_RST_RTC`. Function-like
helpers are none. Value shape: literal numeric range 0..29 across 28 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by `RESET_K210_SYSCTL_H`;
after preprocessing, DTS C-preprocessor users and C drivers see only the constants and any packing
helpers. Comment-delimited groups or observed macro clusters are `K210 group`, which is the intended
lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 42 lines long. Notable source comments include `Kendryte K210 SoC system controller
K210_SYSCTL_SOFT_RESET register bits. Taken from Kendryte SDK (kendryte-standalone-sdk).`,
`RESET_K210_SYSCTL_H`. Example value clusters are K210: `K210_RST_ROM=0`, `K210_RST_DMA=1`,
`K210_RST_AI=2`, `K210_RST_DVP=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `K210_RST_ROM`,
`K210_RST_DMA`, `K210_RST_AI`, `K210_RST_DVP`, `K210_RST_FFT`, `K210_RST_GPIO`, `K210_RST_SPI0`,
`K210_RST_SPI1`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/k210-rst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-infracfg.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-infracfg.h

Purpose: `mediatek,mt6735-infracfg.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 20 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT6735 (20). Representative constants are
`MT6735_INFRA_RST0_EMI_REG`, `MT6735_INFRA_RST0_DRAMC0_AO`, `MT6735_INFRA_RST0_AP_CIRQ_EINT`,
`MT6735_INFRA_RST0_APXGPT`, `MT6735_INFRA_RST0_SCPSYS`, `MT6735_INFRA_RST0_KP`,
`MT6735_INFRA_RST0_PMIC_WRAP`, `MT6735_INFRA_RST0_CLDMA_AO_TOP`, `...`,
`MT6735_INFRA_RST0_EMI_AO_REG`, `MT6735_INFRA_RST0_CCIF_AO`, `MT6735_INFRA_RST0_TRNG`,
`MT6735_INFRA_RST0_SYS_CIRQ`, `MT6735_INFRA_RST0_GCE`, `MT6735_INFRA_RST0_M4U`,
`MT6735_INFRA_RST0_CCIF1`, `MT6735_INFRA_RST0_CLDMA_TOP_PD`. Function-like helpers are none. Value
shape: literal numeric range 0..19 across 20 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_MT6735_INFRACFG_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MT6735 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 27 lines long. Notable source comments include none. Example value clusters are MT6735:
`MT6735_INFRA_RST0_EMI_REG=0`, `MT6735_INFRA_RST0_DRAMC0_AO=1`, `MT6735_INFRA_RST0_AP_CIRQ_EINT=2`,
`MT6735_INFRA_RST0_APXGPT=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT6735_INFRA_RST0_EMI_REG`, `MT6735_INFRA_RST0_DRAMC0_AO`, `MT6735_INFRA_RST0_AP_CIRQ_EINT`,
`MT6735_INFRA_RST0_APXGPT`, `MT6735_INFRA_RST0_SCPSYS`, `MT6735_INFRA_RST0_KP`,
`MT6735_INFRA_RST0_PMIC_WRAP`, `MT6735_INFRA_RST0_CLDMA_AO_TOP`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-infracfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-mfgcfg.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-mfgcfg.h

Purpose: `mediatek,mt6735-mfgcfg.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT6735 (2). Representative constants are
`MT6735_MFG_RST0_AXI`, `MT6735_MFG_RST0_G3D`, `MT6735_MFG_RST0_AXI`, `MT6735_MFG_RST0_G3D`.
Function-like helpers are none. Value shape: literal numeric range 0..1 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_MT6735_MFGCFG_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MT6735 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 9 lines long. Notable source comments include `_DT_BINDINGS_RESET_MT6735_MFGCFG_H`.
Example value clusters are MT6735: `MT6735_MFG_RST0_AXI=0`, `MT6735_MFG_RST0_G3D=1`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `MT6735_MFG_RST0_AXI`,
`MT6735_MFG_RST0_G3D`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-mfgcfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-pericfg.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-pericfg.h

Purpose: `mediatek,mt6735-pericfg.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 23 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT6735 (23). Representative constants are
`MT6735_PERI_RST0_UART0`, `MT6735_PERI_RST0_UART1`, `MT6735_PERI_RST0_UART2`,
`MT6735_PERI_RST0_UART3`, `MT6735_PERI_RST0_UART4`, `MT6735_PERI_RST0_BTIF`,
`MT6735_PERI_RST0_DISP_PWM_PERI`, `MT6735_PERI_RST0_PWM`, `...`, `MT6735_PERI_RST0_MSDC0`,
`MT6735_PERI_RST0_MSDC1`, `MT6735_PERI_RST0_I2C0`, `MT6735_PERI_RST0_I2C1`, `MT6735_PERI_RST0_I2C2`,
`MT6735_PERI_RST0_I2C3`, `MT6735_PERI_RST0_USB`, `MT6735_PERI_RST1_SPI0`. Function-like helpers are
none. Value shape: literal numeric range 0..22 across 23 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_MT6735_PERICFG_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MT6735 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 31 lines long. Notable source comments include none. Example value clusters are MT6735:
`MT6735_PERI_RST0_UART0=0`, `MT6735_PERI_RST0_UART1=1`, `MT6735_PERI_RST0_UART2=2`,
`MT6735_PERI_RST0_UART3=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT6735_PERI_RST0_UART0`, `MT6735_PERI_RST0_UART1`, `MT6735_PERI_RST0_UART2`,
`MT6735_PERI_RST0_UART3`, `MT6735_PERI_RST0_UART4`, `MT6735_PERI_RST0_BTIF`,
`MT6735_PERI_RST0_DISP_PWM_PERI`, `MT6735_PERI_RST0_PWM`. Test signals include DTS compile checks,
reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-pericfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-vdecsys.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-vdecsys.h

Purpose: `mediatek,mt6735-vdecsys.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT6735 (2). Representative constants are
`MT6735_VDEC_RST0_VDEC`, `MT6735_VDEC_RST1_SMI_LARB1`, `MT6735_VDEC_RST0_VDEC`,
`MT6735_VDEC_RST1_SMI_LARB1`. Function-like helpers are none. Value shape: literal numeric range
0..1 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_MT6735_VDECSYS_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MT6735 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 9 lines long. Notable source comments include `_DT_BINDINGS_RESET_MT6735_VDECSYS_H`.
Example value clusters are MT6735: `MT6735_VDEC_RST0_VDEC=0`, `MT6735_VDEC_RST1_SMI_LARB1=1`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT6735_VDEC_RST0_VDEC`, `MT6735_VDEC_RST1_SMI_LARB1`. Test signals include DTS compile checks,
reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-vdecsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-wdt.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-wdt.h

Purpose: `mediatek,mt6735-wdt.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 10 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT6735 (10). Representative constants are
`MT6735_TOPRGU_MM_RST`, `MT6735_TOPRGU_MFG_RST`, `MT6735_TOPRGU_VENC_RST`, `MT6735_TOPRGU_VDEC_RST`,
`MT6735_TOPRGU_IMG_RST`, `MT6735_TOPRGU_MD_RST`, `MT6735_TOPRGU_CONN_RST`,
`MT6735_TOPRGU_C2K_SW_RST`, `MT6735_TOPRGU_VENC_RST`, `MT6735_TOPRGU_VDEC_RST`,
`MT6735_TOPRGU_IMG_RST`, `MT6735_TOPRGU_MD_RST`, `MT6735_TOPRGU_CONN_RST`,
`MT6735_TOPRGU_C2K_SW_RST`, `MT6735_TOPRGU_C2K_RST`, `MT6735_TOPRGU_RST_NUM`. Function-like helpers
are none. Value shape: literal numeric range 1..15 across 10 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_MEDIATEK_MT6735_WDT_H_`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `MT6735 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 17 lines long. Notable source comments include none. Example value clusters are MT6735:
`MT6735_TOPRGU_MM_RST=1`, `MT6735_TOPRGU_MFG_RST=2`, `MT6735_TOPRGU_VENC_RST=3`,
`MT6735_TOPRGU_VDEC_RST=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `MT6735_TOPRGU_MM_RST`,
`MT6735_TOPRGU_MFG_RST`, `MT6735_TOPRGU_VENC_RST`, `MT6735_TOPRGU_VDEC_RST`,
`MT6735_TOPRGU_IMG_RST`, `MT6735_TOPRGU_MD_RST`, `MT6735_TOPRGU_CONN_RST`,
`MT6735_TOPRGU_C2K_SW_RST`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-wdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6795-resets.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6795-resets.h

Purpose: `mediatek,mt6795-resets.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 35 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT6795 (35). Representative constants are
`MT6795_INFRA_RST0_SCPSYS_RST`, `MT6795_INFRA_RST0_PMIC_WRAP_RST`, `MT6795_INFRA_RST1_MIPI_DSI_RST`,
`MT6795_INFRA_RST1_MIPI_CSI_RST`, `MT6795_INFRA_RST1_MM_IOMMU_RST`,
`MT6795_MMSYS_SW0_RST_B_SMI_COMMON`, `MT6795_MMSYS_SW0_RST_B_SMI_LARB`,
`MT6795_MMSYS_SW0_RST_B_CAM_MDP`, `...`, `MT6795_TOPRGU_IMG_SW_RST`, `MT6795_TOPRGU_DDRPHY_SW_RST`,
`MT6795_TOPRGU_MD_SW_RST`, `MT6795_TOPRGU_INFRA_AO_SW_RST`, `MT6795_TOPRGU_MD_LITE_SW_RST`,
`MT6795_TOPRGU_APMIXED_SW_RST`, `MT6795_TOPRGU_PWRAP_SPI_CTL_RST`, `MT6795_TOPRGU_SW_RST_NUM`.
Function-like helpers are none. Value shape: literal numeric range 0..13 across 35 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_MT6795`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `INFRACFG resets`, `MMSYS resets`, `PERICFG resets`, `TOPRGU resets`, which is the intended
lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 53 lines long. Notable source comments include `INFRACFG resets`, `MMSYS resets`,
`PERICFG resets`, `TOPRGU resets`, `_DT_BINDINGS_RESET_CONTROLLER_MT6795`. Example value clusters
are MT6795: `MT6795_INFRA_RST0_SCPSYS_RST=0`, `MT6795_INFRA_RST0_PMIC_WRAP_RST=1`,
`MT6795_INFRA_RST1_MIPI_DSI_RST=2`, `MT6795_INFRA_RST1_MIPI_CSI_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT6795_INFRA_RST0_SCPSYS_RST`, `MT6795_INFRA_RST0_PMIC_WRAP_RST`, `MT6795_INFRA_RST1_MIPI_DSI_RST`,
`MT6795_INFRA_RST1_MIPI_CSI_RST`, `MT6795_INFRA_RST1_MM_IOMMU_RST`,
`MT6795_MMSYS_SW0_RST_B_SMI_COMMON`, `MT6795_MMSYS_SW0_RST_B_SMI_LARB`,
`MT6795_MMSYS_SW0_RST_B_CAM_MDP`. Test signals include DTS compile checks, reset-controller probe,
driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6795-resets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt7988-resets.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt7988-resets.h

Purpose: `mediatek,mt7988-resets.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT7988 (3). Representative constants are
`MT7988_ETHWARP_RST_SWITCH`, `MT7988_INFRA_RST0_PEXTP_MAC_SWRST`,
`MT7988_INFRA_RST1_THERM_CTRL_SWRST`, `MT7988_ETHWARP_RST_SWITCH`,
`MT7988_INFRA_RST0_PEXTP_MAC_SWRST`, `MT7988_INFRA_RST1_THERM_CTRL_SWRST`. Function-like helpers are
none. Value shape: literal numeric range 0..1 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_MT7988`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `ETHWARP resets`, `INFRA resets`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 19 lines long. Notable source comments include `ETHWARP resets`, `INFRA resets`,
`_DT_BINDINGS_RESET_CONTROLLER_MT7988`. Example value clusters are MT7988:
`MT7988_ETHWARP_RST_SWITCH=0`, `MT7988_INFRA_RST0_PEXTP_MAC_SWRST=0`,
`MT7988_INFRA_RST1_THERM_CTRL_SWRST=1`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT7988_ETHWARP_RST_SWITCH`, `MT7988_INFRA_RST0_PEXTP_MAC_SWRST`,
`MT7988_INFRA_RST1_THERM_CTRL_SWRST`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt7988-resets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt8196-resets.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt8196-resets.h

Purpose: `mediatek,mt8196-resets.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 10 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT8196 (10). Representative constants are
`MT8196_PEXTP0_RST0_PCIE0_MAC`, `MT8196_PEXTP0_RST0_PCIE0_PHY`, `MT8196_PEXTP1_RST0_PCIE1_MAC`,
`MT8196_PEXTP1_RST0_PCIE1_PHY`, `MT8196_PEXTP1_RST0_PCIE2_MAC`, `MT8196_PEXTP1_RST0_PCIE2_PHY`,
`MT8196_UFSAO_RST0_UFS_MPHY`, `MT8196_UFSAO_RST1_UFS_UNIPRO`, `MT8196_PEXTP1_RST0_PCIE1_MAC`,
`MT8196_PEXTP1_RST0_PCIE1_PHY`, `MT8196_PEXTP1_RST0_PCIE2_MAC`, `MT8196_PEXTP1_RST0_PCIE2_PHY`,
`MT8196_UFSAO_RST0_UFS_MPHY`, `MT8196_UFSAO_RST1_UFS_UNIPRO`, `MT8196_UFSAO_RST1_UFS_CRYPTO`,
`MT8196_UFSAO_RST1_UFSHCI`. Function-like helpers are none. Value shape: literal numeric range 0..3
across 10 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_MT8196`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PEXTP0 resets`, `PEXTP1 resets`, `UFS resets`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 26 lines long. Notable source comments include `PEXTP0 resets`, `PEXTP1 resets`, `UFS
resets`, `_DT_BINDINGS_RESET_CONTROLLER_MT8196`. Example value clusters are MT8196:
`MT8196_PEXTP0_RST0_PCIE0_MAC=0`, `MT8196_PEXTP0_RST0_PCIE0_PHY=1`,
`MT8196_PEXTP1_RST0_PCIE1_MAC=0`, `MT8196_PEXTP1_RST0_PCIE1_PHY=1`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT8196_PEXTP0_RST0_PCIE0_MAC`, `MT8196_PEXTP0_RST0_PCIE0_PHY`, `MT8196_PEXTP1_RST0_PCIE1_MAC`,
`MT8196_PEXTP1_RST0_PCIE1_PHY`, `MT8196_PEXTP1_RST0_PCIE2_MAC`, `MT8196_PEXTP1_RST0_PCIE2_PHY`,
`MT8196_UFSAO_RST0_UFS_MPHY`, `MT8196_UFSAO_RST1_UFS_UNIPRO`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt8196-resets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt2701-resets.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt2701-resets.h

Purpose: `mt2701-resets.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 64 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT2701 (64). Representative constants are
`MT2701_INFRA_EMI_REG_RST`, `MT2701_INFRA_DRAMC0_A0_RST`, `MT2701_INFRA_FHCTL_RST`,
`MT2701_INFRA_APCIRQ_EINT_RST`, `MT2701_INFRA_APXGPT_RST`, `MT2701_INFRA_SCPSYS_RST`,
`MT2701_INFRA_KP_RST`, `MT2701_INFRA_PMIC_WRAP_RST`, `...`, `MT2701_HIFSYS_PCIE1_RST`,
`MT2701_HIFSYS_PCIE2_RST`, `MT2701_ETHSYS_SYS_RST`, `MT2701_ETHSYS_MCM_RST`, `MT2701_ETHSYS_FE_RST`,
`MT2701_ETHSYS_GMAC_RST`, `MT2701_ETHSYS_PPE_RST`, `MT2701_G3DSYS_CORE_RST`. Function-like helpers
are none. Value shape: literal numeric range 0..38 across 64 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_MT2701`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `INFRACFG resets`, `PERICFG resets`, `TOPRGU resets`, `HIFSYS resets`, `ETHSYS resets`, `G3DSYS
resets`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 85 lines long. Notable source comments include `INFRACFG resets`, `PERICFG resets`,
`TOPRGU resets`, `HIFSYS resets`, `ETHSYS resets`, `G3DSYS resets`. Example value clusters are
MT2701: `MT2701_INFRA_EMI_REG_RST=0`, `MT2701_INFRA_DRAMC0_A0_RST=1`, `MT2701_INFRA_FHCTL_RST=2`,
`MT2701_INFRA_APCIRQ_EINT_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT2701_INFRA_EMI_REG_RST`, `MT2701_INFRA_DRAMC0_A0_RST`, `MT2701_INFRA_FHCTL_RST`,
`MT2701_INFRA_APCIRQ_EINT_RST`, `MT2701_INFRA_APXGPT_RST`, `MT2701_INFRA_SCPSYS_RST`,
`MT2701_INFRA_KP_RST`, `MT2701_INFRA_PMIC_WRAP_RST`. Test signals include DTS compile checks, reset-
controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt2701-resets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt2712-resets.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt2712-resets.h

Purpose: `mt2712-resets.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 10 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT2712 (10). Representative constants are
`MT2712_TOPRGU_INFRA_SW_RST`, `MT2712_TOPRGU_MM_SW_RST`, `MT2712_TOPRGU_MFG_SW_RST`,
`MT2712_TOPRGU_VENC_SW_RST`, `MT2712_TOPRGU_VDEC_SW_RST`, `MT2712_TOPRGU_IMG_SW_RST`,
`MT2712_TOPRGU_INFRA_AO_SW_RST`, `MT2712_TOPRGU_USB_SW_RST`, `MT2712_TOPRGU_MFG_SW_RST`,
`MT2712_TOPRGU_VENC_SW_RST`, `MT2712_TOPRGU_VDEC_SW_RST`, `MT2712_TOPRGU_IMG_SW_RST`,
`MT2712_TOPRGU_INFRA_AO_SW_RST`, `MT2712_TOPRGU_USB_SW_RST`, `MT2712_TOPRGU_APMIXED_SW_RST`,
`MT2712_TOPRGU_SW_RST_NUM`. Function-like helpers are none. Value shape: literal numeric range 0..11
across 10 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_MT2712`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MT2712 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 22 lines long. Notable source comments include `_DT_BINDINGS_RESET_CONTROLLER_MT2712`.
Example value clusters are MT2712: `MT2712_TOPRGU_INFRA_SW_RST=0`, `MT2712_TOPRGU_MM_SW_RST=1`,
`MT2712_TOPRGU_MFG_SW_RST=2`, `MT2712_TOPRGU_VENC_SW_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT2712_TOPRGU_INFRA_SW_RST`, `MT2712_TOPRGU_MM_SW_RST`, `MT2712_TOPRGU_MFG_SW_RST`,
`MT2712_TOPRGU_VENC_SW_RST`, `MT2712_TOPRGU_VDEC_SW_RST`, `MT2712_TOPRGU_IMG_SW_RST`,
`MT2712_TOPRGU_INFRA_AO_SW_RST`, `MT2712_TOPRGU_USB_SW_RST`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt2712-resets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt7621-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt7621-reset.h

Purpose: `mt7621-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 26 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT7621 (26). Representative constants are
`MT7621_RST_SYS`, `MT7621_RST_MCM`, `MT7621_RST_HSDMA`, `MT7621_RST_FE`, `MT7621_RST_SPDIFTX`,
`MT7621_RST_TIMER`, `MT7621_RST_INT`, `MT7621_RST_MC`, `...`, `MT7621_RST_ETH`, `MT7621_RST_PCIE0`,
`MT7621_RST_PCIE1`, `MT7621_RST_PCIE2`, `MT7621_RST_AUX_STCK`, `MT7621_RST_CRYPTO`,
`MT7621_RST_SDXC`, `MT7621_RST_PPE`. Function-like helpers are none. Value shape: literal numeric
range 0..31 across 26 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_MT7621_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`MT7621 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 37 lines long. Notable source comments include `DT_BINDING_MT7621_RESET_H`. Example
value clusters are MT7621: `MT7621_RST_SYS=0`, `MT7621_RST_MCM=2`, `MT7621_RST_HSDMA=5`,
`MT7621_RST_FE=6`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `MT7621_RST_SYS`,
`MT7621_RST_MCM`, `MT7621_RST_HSDMA`, `MT7621_RST_FE`, `MT7621_RST_SPDIFTX`, `MT7621_RST_TIMER`,
`MT7621_RST_INT`, `MT7621_RST_MC`. Test signals include DTS compile checks, reset-controller probe,
driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt7621-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt7622-reset.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt7622-reset.h

Purpose: `mt7622-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 64 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT7622 (64). Representative constants are
`MT7622_INFRA_EMI_REG_RST`, `MT7622_INFRA_DRAMC0_A0_RST`, `MT7622_INFRA_APCIRQ_EINT_RST`,
`MT7622_INFRA_APXGPT_RST`, `MT7622_INFRA_SCPSYS_RST`, `MT7622_INFRA_PMIC_WRAP_RST`,
`MT7622_INFRA_IRRX_RST`, `MT7622_INFRA_EMI_RST`, `...`, `MT7622_ETHSYS_SYS_RST`,
`MT7622_ETHSYS_MCM_RST`, `MT7622_ETHSYS_HSDMA_RST`, `MT7622_ETHSYS_FE_RST`,
`MT7622_ETHSYS_GMAC_RST`, `MT7622_ETHSYS_EPHY_RST`, `MT7622_ETHSYS_CRYPTO_RST`,
`MT7622_ETHSYS_PPE_RST`. Function-like helpers are none. Value shape: literal numeric range 0..36
across 64 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_MT7622`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `INFRACFG resets`, `PERICFG Subsystem resets`, `TOPRGU resets`, `PCIe/SATA Subsystem resets`,
`SSUSB Subsystem resets`, `ETHSYS Subsystem resets`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 86 lines long. Notable source comments include `INFRACFG resets`, `PERICFG Subsystem
resets`, `TOPRGU resets`, `PCIe/SATA Subsystem resets`, `SSUSB Subsystem resets`, `ETHSYS Subsystem
resets`. Example value clusters are MT7622: `MT7622_INFRA_EMI_REG_RST=0`,
`MT7622_INFRA_DRAMC0_A0_RST=1`, `MT7622_INFRA_APCIRQ_EINT_RST=3`, `MT7622_INFRA_APXGPT_RST=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT7622_INFRA_EMI_REG_RST`, `MT7622_INFRA_DRAMC0_A0_RST`, `MT7622_INFRA_APCIRQ_EINT_RST`,
`MT7622_INFRA_APXGPT_RST`, `MT7622_INFRA_SCPSYS_RST`, `MT7622_INFRA_PMIC_WRAP_RST`,
`MT7622_INFRA_IRRX_RST`, `MT7622_INFRA_EMI_RST`. Test signals include DTS compile checks, reset-
controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt7622-reset.h -->
