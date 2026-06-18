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
