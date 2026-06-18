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
