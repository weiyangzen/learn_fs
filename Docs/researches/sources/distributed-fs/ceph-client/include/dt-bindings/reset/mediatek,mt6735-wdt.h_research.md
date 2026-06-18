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
