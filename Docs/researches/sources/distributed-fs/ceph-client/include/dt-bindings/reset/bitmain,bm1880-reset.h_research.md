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
