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
