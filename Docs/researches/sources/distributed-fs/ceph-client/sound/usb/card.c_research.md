# sources/distributed-fs/ceph-client/sound/usb/card.c

## Purpose
Main generic ALSA USB Audio driver entry point. It owns module parameters, card creation and naming, interface aggregation, stream/mixer/MIDI creation, quirk aliasing, platform offload hooks, disconnect, shutdown locking, autosuspend, and PM suspend/resume.

## Important APIs, Types, and Functions
Exported platform/offload APIs are `snd_usb_register_platform_ops()`, `snd_usb_unregister_platform_ops()`, `snd_usb_rediscover_devices()`, and `snd_usb_find_suppported_substream()`. Shutdown/power APIs are `snd_usb_lock_shutdown()`, `snd_usb_unlock_shutdown()`, `snd_usb_autoresume()`, and `snd_usb_autosuspend()`. Core internals include `usb_audio_probe()`, `usb_audio_disconnect()`, `__usb_audio_disconnect()`, `snd_usb_audio_create()`, `snd_usb_create_streams()`, `snd_usb_create_stream()`, `try_to_register_card()`, `find_last_interface()`, `get_alias_id()`, `get_alias_quirk()`, `usb_audio_suspend()`, and `usb_audio_resume()`.

## Control Flow
Probe applies quirk aliases and boot quirks, then under `register_mutex` either finds an existing chip for the USB device or allocates a new ALSA card slot matching module vid/pid/enable filters. New chips initialize lists, flags, names, proc entries, and card private free. Probe claims/creates quirk-specific interfaces when required, otherwise parses normal UAC v1/v2/v3 control descriptors to discover audio streaming and MIDI interfaces, creates mixers, optionally delays card registration until the last matching interface, stores intfdata, increments interface count, and calls platform connect callbacks.

Stream creation handles MIDI streaming interfaces via `snd_usb_midi_v2_create()` and audio streaming interfaces via `snd_usb_parse_audio_interface()`, claiming unused interfaces for the USB audio driver. UAC v1 uses `baInterfaceNr[]`; UAC v2/v3 uses interface association descriptors and validates UAC3 BADD profile. Disconnect uses `shutdown` and `usage_count` to wait for protected tasks, disconnects ALSA, releases PCM endpoints, MIDI, media, and mixers, decrements interface count, and frees the card only after the final interface disappears. Suspend/resume fan out to PCM, endpoint, MIDI, mixer, MIDI2, media/platform hooks, and ALSA power state.

## State and Persistence
Global arrays and parameters persist module-wide: `usb_chip[]`, module card indexes/ids/enables, vid/pid filters, device setup, quirk alias/delayed-register/implicit-feedback flags, and platform ops. Per-card `struct snd_usb_audio` persists in card private data and owns lists of PCM streams, endpoints, interface refs, clock refs, MIDI devices, MIDI2 devices, and mixers, plus active/shutdown/usage counters and PM state.

## Dependencies and Integration Points
Integrates most of the generic USB audio subtree: `stream.c`, `format.c`, `pcm.c`, `endpoint.c`, `mixer.c`, `midi.c`, `midi2.c`, `quirks.c`, `proc.c`, `media.c`, and `power.c`. Exposes platform ops for audio offload users such as Qualcomm sideband drivers. Uses `quirks-table.h` in the USB id table.

## Risks
Probe/disconnect are multi-interface and heavily stateful; refcount, `num_interfaces`, and delayed registration bugs can expose partial cards or free too early. `platform_ops` callbacks run under `register_mutex` in several paths and must avoid deadlocks. Module quirk parameters can alter device behavior at runtime. Shutdown locking depends on all long operations using `snd_usb_lock_shutdown()`. UAC descriptor parsing is security-sensitive because it processes device-supplied descriptors.

## Test Signals
Test UAC1/UAC2/UAC3 devices, MIDI-only interfaces, quirked devices, delayed register option, quirk alias option, multiple control interfaces, disconnect during PCM/MIDI/mixer operations, autosuspend/resume, system suspend/resume, platform ops registration/rediscovery, media-controller sharing, and malformed descriptor validation.
