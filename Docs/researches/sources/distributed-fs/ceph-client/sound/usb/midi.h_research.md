# sources/distributed-fs/ceph-client/sound/usb/midi.h

## Purpose
`midi.h` is the public internal header for the USB-audio legacy MIDI 1.0 helper. It defines endpoint quirk metadata and declares creation/lifecycle functions used by USB-audio and specialized USB sound drivers.

## Important APIs, Types, And Macros
`MIDI_MAX_ENDPOINTS` limits a MIDI interface to two endpoint groups. `struct snd_usb_midi_endpoint_info` describes fixed endpoint numbers, interrupt intervals, cable bitmasks, and associated jack IDs for quirks. `__snd_usbmidi_create()` allows callers to pass an explicit USB ID and rawmidi device counter; `snd_usbmidi_create()` is the common wrapper. Lifecycle declarations cover input stop/start, disconnect, suspend, and resume.

## Control Flow And State
The header provides no implementation except the wrapper that calls `__snd_usbmidi_create(card, iface, midi_list, quirk, 0, NULL)`. Its comments document the expected `quirk->data` shape for standard, fixed endpoint, Yamaha, Midiman, composite, raw, Emagic, CME, and Akai-style quirk types.

## State And Persistence
No persistent state exists. The endpoint info structure is copied by `midi.c` during creation and drives runtime endpoint/cable construction.

## Dependencies And Integration Points
The header is consumed by USB-audio card setup and miscellaneous drivers such as UA-101. It relies on ALSA card/list types and quirk definitions from the surrounding USB-audio code.

## Risks And Edge Cases
Incorrect quirk data layout can misconfigure endpoint direction, intervals, or cable masks. The two-endpoint limit is baked into structure arrays and creation logic. Associated jack IDs use signed 16-bit values, with `-1` used internally to avoid jack-name lookup.

## Test Signals
Compile users with fixed and standard MIDI creation paths. Validate quirk structures for endpoint masks, intervals, and jack IDs; ensure rawmidi numbering works for callers using `__snd_usbmidi_create()` with a shared counter.
