# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-wsa-macro.h

## Purpose

`lpass-wsa-macro.h` is the public header for the WSA macro speaker-mode control exported by `lpass-wsa-macro.c`. It defines the small speaker-mode enum used by callers and declares the exported function that applies the mode to a WSA component.

## Important APIs, types, and functions

- The anonymous enum defines `WSA_MACRO_SPKR_MODE_DEFAULT` and `WSA_MACRO_SPKR_MODE_1`. Mode 1 is documented as compander gain 12 dB and smart boost max 5.5 V.
- `int wsa_macro_set_spkr_mode(struct snd_soc_component *component, int mode);` is the cross-file API. The implementation stores the selected mode in `struct wsa_macro` and writes compander/smart-boost register fields.

## Control flow

Consumers include this header, obtain or already hold a `struct snd_soc_component *` for the WSA macro, and call `wsa_macro_set_spkr_mode()` with one of the enum values. The implementation handles default fallback for unknown values by applying default-mode hardware settings.

## State and persistence behavior

The header itself has no state. Its function declaration affects `lpass-wsa-macro.c` state by changing `wsa->spkr_mode`, which later influences ear-speaker gain compensation in DAPM speaker path events. Hardware register writes are cached through the WSA regmap implementation.

## Dependencies and integration points

The declaration depends on the ASoC `struct snd_soc_component` type being visible to the including C file. In practice this header is part of the Qualcomm LPASS codec/machine-driver integration surface and is included by `lpass-wsa-macro.c`; other codec helpers can call the exported symbol if they need to synchronize speaker mode with board or amplifier configuration.

## Risks and edge cases

- The enum is anonymous and not type-safe, so any integer can be passed to `wsa_macro_set_spkr_mode()`. Unknown values fall back to default behavior in the implementation rather than returning an error despite the function comment saying `-EINVAL` is possible.
- The header does not include `<sound/soc.h>` or forward-declare `struct snd_soc_component`; callers must include compatible ASoC declarations first.
- The comment documents only mode 1. New modes would require synchronized updates to this header, the implementation, and any userspace or machine-driver assumptions.

## Test signals

Build coverage should verify that all users include the needed ASoC declarations before this header. Runtime tests should call the API with default, mode 1, and invalid values, then confirm WSA compander/boost registers and later DAPM speaker-gain compensation match the selected mode.
