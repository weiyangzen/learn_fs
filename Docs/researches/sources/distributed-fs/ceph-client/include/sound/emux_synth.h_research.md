# sources/distributed-fs/ceph-client/include/sound/emux_synth.h

## Purpose
This header defines the generic ALSA emux wavetable synthesizer core used by multiple hardware backends.

## Important APIs, Types, and Functions
`struct snd_emux_operators` provides hardware callbacks for owner setup, sample memory reset/load/free, note trigger/release/update/terminate, voice-volume calculation, and optional OSS hooks. `struct snd_emux` is the root object containing card/hw pointers, max voices, voice array, ports, callback table, soundfont list, sequencer client/ports, timers, memory header, proc entry, and OSS synth pointer. `struct snd_emux_port` tracks per-port MIDI channel state, mode, attenuation, drum flags, controls, and optional effect table. `struct snd_emux_voice` tracks each hardware voice, state flags, note/key/velocity, soundfont zone, MIDI channel, port, backend pointer, timing, raw registers, and computed modulation targets. Public functions create/register/free emux instances and lock/unlock/terminate voices.

## Control Flow
Backend drivers allocate `snd_emux`, fill operators and voice limits, then register it with ALSA sequencer. Incoming MIDI/OSS events allocate voices, select soundfont zones, call backend trigger/update callbacks, and later release or terminate voices. Timers manage pending note-offs and voice aging.

## State and Persistence
Emux maintains in-memory synth state: soundfont zones, active voices, ports, MIDI channel state, effect tables, timers, and memory allocation metadata. Hardware sample memory is backend-specific and volatile. There is no disk persistence.

## Dependencies and Integration Points
It depends on ALSA sequencer, soundfont, MIDI emulation, OSS sequencer compatibility, and virtual MIDI APIs. Backends include EMU8000 and EMU10K1 synth drivers.

## Risks and Edge Cases
Voice states combine bit flags and require careful locking to avoid double allocation or stale note release. Raw effect support is conditional. Backend callbacks must tolerate termination during pending note-off timers. OSS modes add compatibility constraints.

## Test Signals
Sequencer registration, MIDI polyphony, sustain/release behavior, voice locking, soundfont load/free, port modes, OSS compatibility, and stress with max voices/ports validate this layer.
