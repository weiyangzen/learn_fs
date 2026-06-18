<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_midi_event.h -->
# sources/distributed-fs/ceph-client/include/sound/seq_midi_event.h

## Purpose
`seq_midi_event.h` defines the MIDI byte stream to ALSA sequencer event encoder/decoder.

## Important APIs, types, and functions
`MAX_MIDI_EVENT_BUF` is 256. `struct snd_midi_event` stores encode/decode queue length, read count, event type, running status command, no-status flag, buffer size, buffer pointer, and spinlock. APIs include `snd_midi_event_new()`, `snd_midi_event_free()`, reset encode/decode helpers, `snd_midi_event_no_status()`, `snd_midi_event_encode_byte()`, and `snd_midi_event_decode()`.

## Control flow
Raw MIDI bytes are fed one at a time to `snd_midi_event_encode_byte()` until a complete `snd_seq_event` is produced. Sequencer events are converted back to MIDI bytes with `snd_midi_event_decode()`. Reset helpers clear running parser state independently for encode/decode paths.

## State and persistence behavior
Parser state persists in the `snd_midi_event` object across bytes to support running status and multi-byte messages. It is protected by a spinlock and destroyed by `snd_midi_event_free()`.

## Dependencies and integration points
It depends on ALSA sequencer UAPI events and is used by raw MIDI, virtual MIDI, and sequencer bridge code.

## Risks and test signals
Risks include buffer overflow or truncation, running-status mishandling, sysex boundary handling, lock misuse in atomic contexts, and no-status mode surprises. Test signals include all MIDI status classes, running status streams, sysex over maximum buffer size, reset mid-message, and concurrent encode/decode users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_midi_event.h -->
