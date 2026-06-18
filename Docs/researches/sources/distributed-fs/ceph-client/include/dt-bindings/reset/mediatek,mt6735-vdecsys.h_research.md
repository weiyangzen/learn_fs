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
