# sources/distributed-fs/ceph-client/sound/core/seq/seq_midi_event.c

## Purpose
`seq_midi_event.c` converts between raw MIDI 1.0 byte streams and ALSA sequencer events. It implements byte-by-byte MIDI command parsing, running-status-aware decoding back to bytes, sysex buffering, and special handling for 14-bit controls and RPN/NRPN events.

## Important APIs, Types, and Functions
- `snd_midi_event_new()` and `snd_midi_event_free()` allocate/free parser state.
- `snd_midi_event_reset_encode()` resets byte-to-event parser state; `snd_midi_event_reset_decode()` resets running-status output state.
- `snd_midi_event_no_status()` disables running status when callers need explicit status bytes.
- `snd_midi_event_encode_byte()` consumes one raw MIDI byte and reports when a complete sequencer event is ready.
- `snd_midi_event_decode()` converts one sequencer event into raw MIDI bytes.
- Static `status_event[]` maps MIDI status families to sequencer event types, payload lengths, and encode/decode helpers.
- Static `extra_event[]` handles `CONTROL14`, `NONREGPARAM`, and `REGPARAM` sequencer events.

## Control Flow
Encoding treats realtime bytes (`>= 0xf8`) as immediate fixed-length events. Other status bytes reset parser state and determine expected data length. Data bytes either complete the current command, extend sysex, or use running status. Sysex emits a variable-length event when an end marker is seen or the parser buffer fills.

Decoding searches standard and extra event tables, composes the appropriate status byte, and either expands sysex with `snd_seq_expand_var_event()` or emits fixed byte packets. Running status is preserved in `dev->lastcmd` unless system messages or `nostat` force status bytes.

## State and Persistence
Parser state is in `struct snd_midi_event`: buffer pointer/size, `lastcmd`, current parser type, queued length, read offset, `nostat`, and a spinlock. State persists per parser instance, usually per MIDI port or rawmidi file.

## Dependencies and Integration Points
The file is exported to many ALSA MIDI bridges: `seq_midi.c`, `seq_virmidi.c`, and drivers that need MIDI stream conversion. It relies on sequencer variable-event expansion for sysex and `<sound/asoundef.h>` constants for status/control values.

## Risks
Parser buffer size determines sysex chunking; size zero is acceptable for decoders but unsafe for byte encoding if used incorrectly. Running status state is shared per parser, so callers must not reuse one parser for independent streams without locking/resetting. Invalid or unsupported events return `-ENOENT` or are silently skipped depending on path.

## Test Signals
Exercise every status family, realtime interleaving, running status, forced no-status output, sysex chunk and end behavior, 14-bit control output, RPN/NRPN output, invalid format rejection, and concurrent encode/decode reset paths.
