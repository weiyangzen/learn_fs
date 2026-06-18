# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-a1-audio-reset.h

Purpose: `amlogic,meson-a1-audio-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 23 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are AUD_RESET (17), AUD_VAD (6). Representative
constants are `AUD_RESET_DDRARB`, `AUD_RESET_TDMIN_A`, `AUD_RESET_TDMIN_B`, `AUD_RESET_TDMIN_LB`,
`AUD_RESET_LOOPBACK`, `AUD_RESET_TDMOUT_A`, `AUD_RESET_TDMOUT_B`, `AUD_RESET_FRDDR_A`, `...`,
`AUD_RESET_TOACODEC`, `AUD_RESET_CLKTREE`, `AUD_VAD_RESET_DDRARB`, `AUD_VAD_RESET_PDM`,
`AUD_VAD_RESET_TDMIN_VAD`, `AUD_VAD_RESET_TODDR_VAD`, `AUD_VAD_RESET_TOVAD`,
`AUD_VAD_RESET_CLKTREE`. Function-like helpers are none. Value shape: literal numeric range 0..31
across 23 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_A1_AUDIO_RESET_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `AUD_RESET group`, `AUD_VAD group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 36 lines long. Notable source comments include
`_DT_BINDINGS_AMLOGIC_MESON_A1_AUDIO_RESET_H`. Example value clusters are AUD_RESET:
`AUD_RESET_DDRARB=0`, `AUD_RESET_TDMIN_A=1`, `AUD_RESET_TDMIN_B=2`, `AUD_RESET_TDMIN_LB=3`; AUD_VAD:
`AUD_VAD_RESET_DDRARB=0`, `AUD_VAD_RESET_PDM=1`, `AUD_VAD_RESET_TDMIN_VAD=2`,
`AUD_VAD_RESET_TODDR_VAD=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `AUD_RESET_DDRARB`,
`AUD_RESET_TDMIN_A`, `AUD_RESET_TDMIN_B`, `AUD_RESET_TDMIN_LB`, `AUD_RESET_LOOPBACK`,
`AUD_RESET_TDMOUT_A`, `AUD_RESET_TDMOUT_B`, `AUD_RESET_FRDDR_A`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
