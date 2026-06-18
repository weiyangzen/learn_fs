# sources/distributed-fs/ceph-client/sound/usb/caiaq/midi.h

## Purpose
Declares CAIAQ rawmidi initialization and data callbacks.

## Important APIs, Types, and Functions
Provides `snd_usb_caiaq_midi_init()`, `snd_usb_caiaq_midi_handle_input()`, and `snd_usb_caiaq_midi_output_done()`.

## Control Flow
No executable logic. `device.c` calls init and uses output completion callback in the MIDI output URB.

## State and Persistence
No header-owned state.

## Dependencies and Integration Points
Requires `struct snd_usb_caiaqdev` and `struct urb` declarations from included compilation context.

## Risks
Only minimal prototypes are exposed; lifecycle cleanup is implicit through card teardown and URB kill in `device.c`.

## Test Signals
Build and rawmidi enumeration after probe.
