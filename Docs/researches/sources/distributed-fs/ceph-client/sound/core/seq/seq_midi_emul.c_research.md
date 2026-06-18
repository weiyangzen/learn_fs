# sources/distributed-fs/ceph-client/sound/core/seq/seq_midi_emul.c

## Purpose
`seq_midi_emul.c` provides driver-independent MIDI channel state emulation for ALSA sequencer clients. It tracks notes, controllers, RPN/NRPN state, GM/GS/XG sysex modes, drum-channel status, and common controller semantics so hardware or software drivers can consume normalized callbacks.

## Important APIs, Types, and Functions
- `snd_midi_process_event()` is the main event interpreter. It updates channel state and calls driver callbacks in `struct snd_midi_op`.
- `snd_midi_channel_set_clear()` resets all channels to GM-like defaults.
- `snd_midi_channel_alloc_set()` and `snd_midi_channel_free_set()` allocate/free channel sets.
- `do_control()` handles controller changes, sustain/sostenuto, data entry, RPN/NRPN selection, reset controllers, all-sounds-off, and all-notes-off.
- `sysex()` parses GM on, GS reset/drum/reverb/chorus/master-volume, and XG on messages.
- `rpn()` and `nrpn()` parse registered/nonregistered parameter changes.

## Control Flow
`snd_midi_process_event()` determines the target channel for channel events, normalizes note-on with velocity zero into note-off, filters invalid notes/channels, and switches on event type. Note events update `chan->note[]` and call `note_on`, `note_off`, or `key_press`. Controller events pass through `do_control()`, where switch-type controllers are normalized and special controllers alter note hold/release state or parameter tracking. Sysex events are expanded into a small stack buffer and parsed for known GM/GS/XG macros before optionally invoking the driver's `sysex` callback.

## State and Persistence
State lives in `struct snd_midi_channel_set` and its channel array: note flags, controller values, program, pressure, pitchbend, GM RPN values, GS settings, MIDI mode, and drum-channel flags. It is in-memory only and owned by the driver that allocated the set.

## Dependencies and Integration Points
Uses public ALSA sequencer MIDI emulation types from `<sound/seq_midi_emul.h>`, asoundef controller constants, and `snd_seq_expand_var_event()` for sysex payloads. Hardware synth drivers can route sequencer events through this layer to implement MIDI behavior without duplicating common controller logic.

## Risks
The sysex parser expands into a 64-byte stack buffer, so longer sysex messages are ignored by this emulation layer. Channel set allocation does not initialize every top-level field unless allocation succeeds, so callers should clear or set private data explicitly. Callback ordering around sustain/sostenuto affects stuck-note behavior.

## Test Signals
Good tests include note-on/off including velocity-zero note-on, sustain and sostenuto release sequences, all-notes/off and all-sounds/off, RPN pitch bend range/fine/coarse tuning, GS/XG sysex mode changes, and invalid channel/note filtering.
