# sources/distributed-fs/ceph-client/sound/soc/codecs/madera.h

## Purpose
`madera.h` is the shared public header for Madera-family ASoC codec support. It exposes clock and FLL identifiers, common private data structures, DAPM/control construction macros, exported control tables, DAI operation tables, and helper prototypes used by chip-specific Madera codec drivers and, in a small notifier wrapper, machine drivers.

## Important APIs, types, and data
- Clock and FLL constants define externally visible IDs for `set_sysclk()` and FLL setter calls: `MADERA_FLL*_REFCLK`, `MADERA_FLL*_SYNCCLK`, `MADERA_FLL_SRC_*`, `MADERA_CLK_*`, `MADERA_CLK_SRC_*`, and OUTCLK source IDs.
- `struct madera_priv` is the common codec private state shared with `madera.c`. It owns ADSP instances, the MFD pointer, device pointer, sysclk/asyncclk/dspclk values, per-DAI data, pending power sequencing counters, ADSP rate cache, rate lock, TDM config, and rate-domain reference counts.
- `struct madera_dai_priv` stores the selected clock ID and an ALSA constraint list for one DAI.
- `struct madera_fll_cfg` and `struct madera_fll` describe calculated and persistent FLL state.
- `struct madera_enum` wraps a `soc_enum` with an extra value field for codec-specific enum use.
- DAPM/control macros such as `MADERA_GAINMUX_CONTROLS`, `MADERA_MIXER_CONTROLS`, `MADERA_MUX_ENUMS`, `MADERA_MIXER_ENUMS`, `MADERA_DSP_WIDGETS`, and route helpers allow chip drivers to instantiate large mixer graphs consistently.
- Export declarations cover mixer TLVs/texts/values, rate enums, DFC/ASRC/ISRC enums, input/output ramp enums, ANC enums, DSP trigger muxes, and ADSP rate controls.

## Control flow
This header does not execute code except for two inline notifier wrappers. Its main role is compile-time composition: chip-specific drivers use the macros to declare ASoC controls, widgets, and routes, then register operation callbacks implemented in `madera.c`. `madera_register_notifier()` and `madera_unregister_notifier()` fetch `struct madera_priv` from the component driver data and register or unregister a notifier block on the underlying Madera MFD notifier chain.

## State and persistence behavior
The header defines state layout but does not allocate it. `struct madera_priv` is allocated by chip-specific codec drivers and populated during component probe. `struct madera_fll` instances are usually embedded in those drivers and initialized by `madera_init_fll()`. The notifier inline helpers operate on the MFD notifier chain, so registered blocks persist until explicitly unregistered or the parent device is torn down.

## Dependencies and integration points
The header depends on Linux completions, ASoC core types, Madera platform data, and `wm_adsp.h`. It intentionally exposes `struct wm_adsp` and Madera platform constants to chip-specific codec implementations. The exported functions are implemented by `madera.c`; chip-specific drivers must link against that object and the Madera MFD/register headers.

## Risks and edge cases
- Macro-heavy DAPM declarations rely on exact register spacing and naming conventions; a chip-specific driver passing the wrong base register can silently produce wrong controls/routes.
- Constants such as `MADERA_MAX_DAI`, `MADERA_MAX_ADSP`, `MADERA_N_DOM_GRPS`, and `MADERA_NUM_MIXER_INPUTS` must stay aligned with implementation arrays; `madera.c` has build-time checks for mixer arrays but not for every exported enum family.
- The notifier inline helpers assume `snd_soc_component_get_drvdata()` returns a valid `struct madera_priv` and that `priv->madera` is initialized.
- `struct madera_priv` exposes mutable fields used across DAPM callbacks and hw_params; callers must respect locking expectations documented only in implementation comments.

## Test signals
Compile coverage from all Madera chip drivers is the key signal for this header because it catches macro signature drift and missing exports. Runtime validation should include registering/unregistering machine-driver notifiers, instantiating mixer/DSP widgets from macros, and checking that all exported arrays match the declared sizes.
