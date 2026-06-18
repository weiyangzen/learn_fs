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
