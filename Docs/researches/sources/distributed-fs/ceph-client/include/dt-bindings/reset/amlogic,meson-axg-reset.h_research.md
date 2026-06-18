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
