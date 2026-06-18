<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_midi_emul.h -->
# sources/distributed-fs/ceph-client/include/sound/seq_midi_emul.h

## Purpose
`seq_midi_emul.h` provides MIDI channel-state emulation for ALSA sequencer clients whose hardware does not directly understand MIDI semantics.

## Important APIs, types, and functions
`struct snd_midi_channel` tracks per-channel mode, drum flag, RPN/NRPN selection, aftertouch, channel pressure, program, pitch bend, controllers, note state, and GM RPN values. `struct snd_midi_channel_set` groups channels for one client/port and stores MIDI mode plus GS master volume, chorus, and reverb. `struct snd_midi_op` contains callbacks for note on/off, key pressure, terminate, control, NRPN, and sysex. Helpers include `snd_midi_process_event()`, `snd_midi_channel_set_clear()`, `snd_midi_channel_alloc_set()`, and `snd_midi_channel_free_set()`.

## Control flow
Sequencer events are fed to `snd_midi_process_event()`, which updates channel/controller/note state and invokes driver callbacks with decoded MIDI operations. Drivers allocate a channel set for a port, process events while maintaining state, and clear or free the set on reset/teardown.

## State and persistence behavior
State is in memory per MIDI channel set. It persists across events for correct controller, RPN, pitch-bend, note, drum-channel, and sysex behavior, but is reset by clear/free and is not durable.

## Dependencies and integration points
It depends on `seq_kernel.h` and sequencer events. It integrates software MIDI parsing with hardware synth or emulation backends.

## Risks and test signals
Risks include stale note/controller state after reset, RPN/NRPN interpretation errors, sysex parser coverage gaps, out-of-range channel counts, and callback reentrancy assumptions. Test signals include GM/GS/XG mode sysex, pitch bend and paired controllers, sustain/sostenuto note release, drum-channel changes, NRPN/RPN sequences, and channel-set allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_midi_emul.h -->
