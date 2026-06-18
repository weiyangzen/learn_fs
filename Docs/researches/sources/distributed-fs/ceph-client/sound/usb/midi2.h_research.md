# sources/distributed-fs/ceph-client/sound/usb/midi2.h

## Purpose
`midi2.h` declares USB MIDI 2.0 integration points for USB-audio and provides legacy MIDI 1.0 fallback stubs when `CONFIG_SND_USB_AUDIO_MIDI_V2` is disabled.

## Important APIs, Types, And Macros
When MIDI 2.0 is enabled, it declares `snd_usb_midi_v2_create()`, suspend/resume, disconnect, and free helpers. When disabled, `snd_usb_midi_v2_create()` is an inline wrapper around `__snd_usbmidi_create()` using `chip->midi_list` and `chip->num_rawmidis`; the lifecycle helpers become no-ops.

## Control Flow And State
The header selects compile-time behavior. Enabled builds route USB MIDI interface creation through `midi2.c`, which can still fall back dynamically. Disabled builds always create legacy MIDI 1.0 rawmidi devices and maintain no MIDI 2.0 list state.

## State And Persistence
No state is stored in this header. It affects whether runtime state is stored in `chip->midi_v2_list` or the legacy `chip->midi_list`.

## Dependencies And Integration Points
The header depends on `midi.h` for the legacy fallback and on USB-audio structures supplied by callers. It lets USB-audio core call the same symbol names regardless of configuration.

## Risks And Edge Cases
In disabled builds, suspend/resume/disconnect/free operations for MIDI 2.0 are no-ops by design; callers must still run legacy MIDI lifecycle on `chip->midi_list`. The inline fallback ignores MIDI 2.0 descriptors completely.

## Test Signals
Build both `CONFIG_SND_USB_AUDIO_MIDI_V2=y/m` and disabled configurations. Verify dynamic fallback in enabled builds and direct legacy creation in disabled builds, including rawmidi numbering through `chip->num_rawmidis`.
