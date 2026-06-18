# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-g12a-audio-reset.h

Purpose: `amlogic,meson-g12a-audio-reset.h` is a Devicetree binding header for a reset-controller provider.
It exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 39 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are AUD_RESET (39). Representative constants are
`AUD_RESET_PDM`, `AUD_RESET_TDMIN_A`, `AUD_RESET_TDMIN_B`, `AUD_RESET_TDMIN_C`,
`AUD_RESET_TDMIN_LB`, `AUD_RESET_LOOPBACK`, `AUD_RESET_TODDR_A`, `AUD_RESET_TODDR_B`, `...`,
`AUD_RESET_FRHDMIRX`, `AUD_RESET_FRDDR_D`, `AUD_RESET_TODDR_D`, `AUD_RESET_LOOPBACK_B`,
`AUD_RESET_EARCTX`, `AUD_RESET_EARCRX`, `AUD_RESET_FRDDR_E`, `AUD_RESET_TODDR_E`. Function-like
helpers are none. Value shape: literal numeric range 0..38 across 39 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_G12A_AUDIO_RESET_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `SM1 added resets`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 53 lines long. Notable source comments include `SM1 added resets`. Example value
clusters are AUD_RESET: `AUD_RESET_PDM=0`, `AUD_RESET_TDMIN_A=1`, `AUD_RESET_TDMIN_B=2`,
`AUD_RESET_TDMIN_C=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `AUD_RESET_PDM`,
`AUD_RESET_TDMIN_A`, `AUD_RESET_TDMIN_B`, `AUD_RESET_TDMIN_C`, `AUD_RESET_TDMIN_LB`,
`AUD_RESET_LOOPBACK`, `AUD_RESET_TODDR_A`, `AUD_RESET_TODDR_B`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
