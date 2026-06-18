# sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett.c

## Purpose
`mixer_scarlett.c` implements first-generation Focusrite Scarlett and Focusrite Forte mixer support. It creates ALSA controls for routing, matrix mixer gains, output volumes/mutes, sample clock controls, sync status, and selected input hardware features. The code exists because UAC2 descriptors do not reliably expose the full Scarlett/Forte control surface, matching the behavior of vendor software that also uses model-specific knowledge.

## Important APIs, types, and functions
- `struct scarlett_mixer_elem_enum_info` describes static or dynamically generated enum domains, including start offsets and source-name offsets.
- `struct scarlett_mixer_control` and `struct scarlett_device_info` describe per-model control lists, matrix dimensions, input/output counts, routing support, and initial matrix mux values.
- Forte-specific helpers `forte_set_ctl_value()`, `forte_get_ctl_value()`, `forte_input_gain_*()`, `forte_ctl_enum_*()`, and `forte_ctl_switch_*()` implement controls through `UAC2_CS_MEM` writes to unit `0x3c`, with cached state because device reads may not be supported.
- Scarlett generic callbacks `scarlett_ctl_switch_*()`, `scarlett_ctl_*()`, `scarlett_ctl_enum_*()`, `scarlett_ctl_meter_get()`, and `scarlett_ctl_resume()` implement boolean mute switches, integer gain controls with TLV, static/dynamic enumerations, sync status, and cached resume replay.
- `add_new_ctl()` is the local control factory. It allocates `usb_mixer_elem_info`, fills UAC-like addressing fields, attaches enum metadata in `private_data`, creates an ALSA kcontrol, and registers it with the mixer.
- `add_output_ctls()` creates master pair mute/volume controls and optional left/right output source routing controls.
- `scarlett_controls_create_generic()` builds common master controls and per-model hardware/input/output controls.
- `snd_scarlett_controls_create()` and `snd_forte_controls_create()` are the exported entry points used by `mixer_quirks.c`.

## Control flow
Both exported create functions first require UAC2 (`mixer->protocol` nonzero) and dispatch on USB ID to choose a `scarlett_device_info` table. They call `scarlett_controls_create_generic()`, then create matrix route controls and matrix mix volume controls. Scarlett devices additionally create input capture route controls, sample clock source, sync status, and initialize the sample rate to 48000 Hz through a class CUR write to control `0x29`. Forte creates a smaller matrix and sync status, with Forte-specific input controls from the generic table.

Normal Scarlett `get` and `put` paths call `snd_usb_get_cur_mix_value()` and `snd_usb_set_cur_mix_value()` using fields stored in `usb_mixer_elem_info`: `head.id` becomes the high byte of `wIndex`, `control` contributes to `wValue`, and `idx_off` selects channel/node. Mute switch logic is inverted for user-facing semantics. Gain values are scaled by 256 and biased by `SND_SCARLETT_LEVEL_BIAS` so GUI mixers avoid negative values.

Dynamic route enumerations generate names such as PCM, Analog, S/PDIF, ADAT, Mix, or Off from the model’s offset table. The same enum callbacks are used for matrix mux, output source routing, and capture source routing.

## State and persistence behavior
Most Scarlett controls read current values from the device and rely on `usb_mixer_elem_info` caching performed by the lower mixer helpers for resume replay. `scarlett_ctl_resume()` replays cached per-channel values. Enum resume replays the cached first value. Forte controls explicitly cache writes in `elem->cached` and `elem->cache_val[0]` because `forte_get_ctl_value()` does not actually read hardware and defaults to zero when uncached.

The device info tables are static read-only configuration. `matrix_mux_init` arrays document initial routing expectations but this file does not visibly use them in the read sections; matrix controls are created for userspace to set routes.

## Dependencies and integration points
The file depends on ALSA control/TLV APIs, Linux USB APIs, USB Audio v2 request constants, and local helpers from `usbaudio.h`, `mixer.h`, `helper.h`, `power.h`, and `mixer_scarlett.h`. It integrates with `mixer_quirks.c` for Focusrite USB IDs `0x1235:8010`, `8012`, `8002`, `8004`, `8014`, and `800c`. Newer Scarlett/Clarett generations are intentionally handled by other modules (`mixer_scarlett2.c` or FCP), not by this file.

## Risks and edge cases
- The implementation is model-table driven. Incorrect `matrix_in`, `matrix_out`, offsets, or control codes create wrong ALSA controls or issue writes to the wrong vendor control.
- Forte reads are cache/default based, so after hardware-side changes or a missed write, ALSA may report stale/default values.
- `snd_scarlett_controls_create()` writes a fixed 48000 Hz sample rate during mixer creation, which can interact with runtime audio configuration expectations.
- Some `sprintf()` calls are used where most other paths use bounded formatting; current names are short, but future control names should stay within ALSA ID limits.
- Dynamic enum naming depends on offset ordering and one-based comparisons in `scarlett_generate_name()`. Off-by-one errors are easy when adding devices.
- `scarlett_ctl_meter_get()` uses `elem->channels` as transfer length even though the buffer is sized for `2 * MAX_CHANNELS`; this is fine for current one-byte sync use but worth checking if reused.

## Test signals
- Probe each supported first-generation Scarlett/Forte model and verify expected control counts and names with `amixer controls`.
- Exercise route enums, matrix volumes, master mute/volume, sample clock source, and sync status through `amixer cget/cset`.
- Suspend/resume after changing routes and gains to confirm cached values replay.
- For Forte, test write/readback expectations carefully because software readback is cache-based rather than hardware-derived.
- USB traces against Scarlett MixControl/Forte Control are useful for validating request numbers, `wValue`, `wIndex`, and payload shape.
