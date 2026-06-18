# sources/distributed-fs/ceph-client/sound/usb/6fire/midi.h

## Purpose
Declares 6Fire rawmidi runtime state and lifecycle functions.

## Important APIs, Types, and Functions
`struct midi_runtime` stores chip pointer, rawmidi instance, active substreams, locks, output URB, serial, buffer, and input callback pointer. Public functions are `usb6fire_midi_init()`, `usb6fire_midi_abort()`, and `usb6fire_midi_destroy()`.

## Control Flow
No executable logic. `comm.c` calls `in_received`; `chip.c` calls lifecycle functions.

## State and Persistence
The runtime persists as `chip->midi`. `in_active` and `buffer_offset` are present but not used by current implementation.

## Dependencies and Integration Points
Includes `common.h`; used by `midi.c`, `comm.c`, and `chip.c`.

## Risks
Unused fields can mislead future changes. Active substream pointers require disconnect/abort ordering to avoid completion callbacks after free.

## Test Signals
Compile plus runtime MIDI open/trigger/abort coverage.
