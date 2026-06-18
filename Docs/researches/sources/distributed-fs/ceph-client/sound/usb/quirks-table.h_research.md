# sources/distributed-fs/ceph-client/sound/usb/quirks-table.h

## Purpose

`quirks-table.h` is the device-ID and descriptor override table included by the ALSA USB audio driver ID table. It exists for USB audio/MIDI hardware whose descriptors are missing, misleading, vendor-specific, or whose alternate-interface layout needs forced handling. The file is intentionally data-heavy: each table entry matches a USB device/interface and optionally attaches a `struct snd_usb_audio_quirk` through `QUIRK_DRIVER_INFO`.

The table is part of probe-time device selection. It does not execute logic directly, but it selects quirk types and inline data consumed by `quirks.c`, `midi.c`, `stream.c`, mixer setup, and endpoint setup.

## Important APIs, Types, And Macros

- `USB_DEVICE_VENDOR_SPEC(vend, prod)` matches a vendor/product only when the interface class is vendor-specific. It prevents quirk handling from applying to unrelated standard interfaces on the same device.
- `USB_AUDIO_DEVICE(vend, prod)` matches USB audio control interfaces by VID/PID and audio class/subclass.
- `QUIRK_DRIVER_INFO` stores a pointer to a compound-literal `struct snd_usb_audio_quirk` in `.driver_info`.
- `QUIRK_DATA_IGNORE`, `QUIRK_DATA_STANDARD_AUDIO`, `QUIRK_DATA_STANDARD_MIDI`, and `QUIRK_DATA_STANDARD_MIXER` encode simple interface actions.
- `QUIRK_DATA_COMPOSITE` creates an array of child `struct snd_usb_audio_quirk` entries terminated by `QUIRK_COMPOSITE_END`.
- `QUIRK_DATA_AUDIOFORMAT` embeds a fixed `struct audioformat`, including endpoint address, format bitmask, channel count, alternate setting, rate table, sync endpoint, implicit feedback flag, and clock ID.
- `QUIRK_DATA_MIDI_FIXED_ENDPOINT`, `QUIRK_DATA_MIDI_MIDIMAN`, and `QUIRK_DATA_MIDI_EMAGIC` embed `struct snd_usb_midi_endpoint_info`.
- Local generator macros such as `YAMAHA_DEVICE`, `YAMAHA_INTERFACE`, `QUIRK_RME_DIGIFACE`, and `QUIRK_AF16RIG` reduce repeated entries for large related device families.

## Control Flow And Data Shape

The file is written as a sequence of initializer entries for a surrounding `struct usb_device_id` array. During USB probing, the kernel USB core matches an entry, and the driver retrieves `.driver_info` as a quirk descriptor. `snd_usb_create_quirk()` then dispatches by `quirk->type`.

Composite entries are the dominant pattern. They describe per-interface actions in order, for example: ignore a broken control or HID-like interface, parse a standard mixer, create fixed playback/capture audio formats, and then create MIDI endpoints. Fixed audio entries are used where the device descriptor cannot be trusted and the driver must provide the ALSA-visible PCM format contract itself.

The table covers broad families: Creative, Yamaha, Roland/Edirol/BOSS, M-Audio/Midiman, MOTU, Emagic, KORG, AKAI, Steinberg, TerraTec, Novation/Focusrite, Native Instruments, Digidesign, TASCAM, Denon, Pioneer/AlphaTheta DJ devices, MacroSilicon capture devices, Fiero, RME Digiface, Arturia AF16Rig, and catch-all MIDI streaming or vendor-specific autodetect matches.

## State And Persistence Behavior

The file contains static, compile-time data only. There is no runtime persistence, locking, allocation, or cleanup here. Runtime state arises after consumers copy or interpret the data. Fixed `rate_table` arrays are compound literals referenced through the quirk data and copied by `create_fixed_stream_quirk()` when needed, which makes the table's lifetime appropriate for static driver data while still allowing mutable per-device `audioformat` instances at probe time.

## Dependencies And Integration Points

This table depends on USB matching macros and ALSA USB audio structures from the surrounding driver includes. It must stay consistent with:

- `enum quirk_type` and `struct snd_usb_audio_quirk` in `usbaudio.h`.
- `snd_usb_create_quirk()` dispatch in `quirks.c`.
- MIDI endpoint quirk handling in the USB MIDI code.
- `struct audioformat` fields consumed by `stream.c`, endpoint setup, format parsing, and PCM setup.
- Boot and flag quirks in `quirks.c`, because some devices have both ID-table quirks and separate VID/PID-specific boot or behavior flags.

## Risks

- A wrong endpoint address, `ep_idx`, `altset_idx`, `sync_ep`, or implicit feedback flag can create silent audio, channel swaps, feedback failures, or probe errors.
- Broad matches such as vendor-specific catch-alls can claim devices that would otherwise work through standard descriptors; ordering and match flags matter.
- `QUIRK_NODEV_INTERFACE` entries intentionally block generic handling for devices owned by another driver; misusing them can make a device disappear.
- Some fixed-format entries encode rates and packet sizes discovered empirically; adding rates without hardware validation can create broken ALSA formats.
- Compound macro definitions obscure initializer boundaries, so syntax errors or missing terminators can affect many entries.

## Test Signals

- Build-test the USB audio driver after edits; initializer syntax and enum/type mismatches are caught at compile time.
- Probe affected devices and inspect `dmesg`, ALSA card creation, PCM device list, MIDI device list, and `/proc/asound/card*/stream*`.
- Exercise playback/capture at every advertised rate/channel count for fixed audio entries.
- For implicit-feedback entries, test simultaneous playback/capture and xrun recovery.
- For broad match changes, test unrelated devices sharing the same vendor ID to catch accidental claiming.
