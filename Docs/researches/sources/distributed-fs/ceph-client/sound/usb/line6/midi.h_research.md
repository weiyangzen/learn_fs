# sources/distributed-fs/ceph-client/sound/usb/line6/midi.h

## Purpose
Declares the Line 6 raw MIDI state object and MIDI initialization/receive APIs.

## Types and APIs
`struct snd_line6_midi` links back to `usb_line6`, tracks active rawmidi receive/transmit substreams, counts active send URBs, protects buffers with a spinlock, provides a send waitqueue, and owns input/output `midi_buffer` instances. `line6_init_midi()` creates rawmidi state and `line6_midi_receive()` forwards incoming MIDI data.

## State, Dependencies, and Risks
The header depends on ALSA rawmidi and `midibuf.h`. Callers must initialize MIDI only for devices with MIDI control capability and must not call receive before `line6->line6midi` is set.

## Test Signals
Build coverage and rawmidi open/trigger/input/output tests validate the declarations.
