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
