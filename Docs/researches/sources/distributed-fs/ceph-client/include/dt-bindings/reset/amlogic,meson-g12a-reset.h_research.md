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
