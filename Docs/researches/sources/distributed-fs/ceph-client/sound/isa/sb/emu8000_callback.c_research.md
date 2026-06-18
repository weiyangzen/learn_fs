# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_callback.c

## Purpose
`emu8000_callback.c` binds the generic ALSA emux sequencer engine to EMU8000 hardware. It provides voice allocation, voice prepare/trigger/release/update/reset/terminate operations, SoundFont sample callbacks, SysEx effect handling, optional OSS emulation ioctl handling, and custom effect loading.

## Important APIs, Types, and Functions
- `snd_emu8000_ops_setup` installs `emu8000_ops` into `hw->emu`.
- Emux operators include `get_voice`, `start_voice`, `trigger_voice`, `release_voice`, `update_voice`, `terminate_voice`, `reset_voice`, `snd_emu8000_sample_new`, `snd_emu8000_sample_free`, `snd_emu8000_sample_reset`, `load_fx`, and `sysex`.
- Hardware setters include `set_pitch`, `set_volume`, `set_pan`, `set_fmmod`, `set_tremfreq`, `set_fm2frq2`, `set_filterQ`, and `snd_emu8000_tweak_voice`.

## Control Flow
When emux needs a voice, `get_voice` ranks channels by off, released/pending, or playing state and reuses the oldest suitable voice, also checking single-shot samples that already reached loop end. `start_voice` silences the channel, programs pitch, envelopes, LFOs, pan, loop points, chorus, filter Q, current address, and target values. `trigger_voice` starts the volume envelope and sets reverb/pitch target. Runtime updates selectively rewrite pitch, volume, pan, modulation, tremolo, LFO2, or filter Q. Release and terminate write release or forced-off envelope values.

## State and Persistence
Voice state is managed by `snd_emux` and per-voice register snapshots. The file mutates hardware registers directly and updates effect mode fields in `struct snd_emu8000` for SysEx/OSS commands. No persistent storage is used.

## Dependencies and Integration Points
It depends on `emu8000_local.h`, ALSA emux, SoundFont sample callbacks from `emu8000_patch.c`, and effect functions from `emu8000.c`. It is loaded as part of `snd-emu8000-synth`.

## Risks and Test Signals
Risks include voice stealing semantics, single-shot completion detection based on CCCA address, signed modulation/pitch clamping, and userspace effect payload handling after a fixed 16-byte header skip. Test signals include MIDI note on/off, voice reuse under polyphony pressure, real-time controller updates for pitch/volume/pan/modulation, GS SysEx chorus/reverb changes, OSS ioctl compatibility when enabled, and SoundFont loading callbacks.
