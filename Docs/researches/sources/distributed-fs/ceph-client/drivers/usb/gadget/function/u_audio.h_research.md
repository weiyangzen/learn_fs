## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_audio.h

Purpose: declares the public interface and configuration structures for the USB gadget ALSA audio utility implemented in `u_audio.c`.

Important APIs and types:
- `FBACK_SLOW_MAX` and `FBACK_FAST_MAX` define default feedback pitch deviation bounds in per-mil units.
- `struct uac_fu_params` describes a UAC Feature Unit: unit ID, mute presence, volume presence, and min/max/resolution in 1/256 dB.
- `struct uac_params` holds playback and capture channel masks, zero-terminated sample-rate arrays of length `UAC_MAX_RATES`, sample sizes, feature-unit params, preallocated request count, and feedback maximum drift.
- `struct g_audio` embeds `usb_function`, endpoint pointers, endpoint max packet sizes, UAC control notification callback, private `snd_uac_chip`, and `uac_params`.
- `func_to_g_audio()` converts a `usb_function` to `g_audio`; `num_channels()` counts enabled bits in a channel mask.
- Declares setup/cleanup, stream start/stop, sample-rate get/set, mute/volume get/set, and suspend APIs.

Control flow and integration:
- UAC function drivers allocate/embed `struct g_audio`, fill `params`, descriptors, endpoint max packet sizes, and `notify`, then call `g_audio_setup()`.
- USB alt-setting changes call `u_audio_start_*()` / `u_audio_stop_*()`.
- USB class control request handlers call get/set helpers for current rate and feature-unit state.

State and persistence:
- This header defines only in-memory runtime/configuration contracts. Actual persistent state lives in the `snd_uac_chip` object allocated by `g_audio_setup()`.
- Rate arrays are fixed-size and use `0` as terminator, so callers must initialize them carefully.

Dependencies:
- Includes USB composite APIs and `uac_common.h` for `UAC_MAX_RATES`.
- Depends on ALSA types indirectly through the opaque `struct snd_uac_chip`.

Risks:
- `num_channels(0)` returns `0`; callers use zero channel masks to suppress stream creation.
- Feature-unit IDs must match descriptors owned by UAC function drivers; mismatch breaks host control routing.
- `req_number` directly affects memory pressure and endpoint queue depth.

Test signals:
- Compile users of the header against UAC1/UAC2 configurations.
- Validate that configfs-provided rates fit within `UAC_MAX_RATES` and are zero-terminated before `g_audio_setup()`.
- Confirm `notify()` receives expected unit/control selector values for ALSA-side mute/volume changes.
