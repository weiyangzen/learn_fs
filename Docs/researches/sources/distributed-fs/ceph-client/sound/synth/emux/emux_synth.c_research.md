# sources/distributed-fs/ceph-client/sound/synth/emux/emux_synth.c

## Purpose
This file is the main EMUX MIDI synthesis engine. It maps MIDI notes to soundfont zones, allocates and prepares hardware voices, handles note-off/key-pressure/controller updates, calculates pitch/volume/pan parameters, terminates voices, and initializes/locks voice records.

## Important APIs, types, and functions
Public callbacks include `snd_emux_note_on`, `snd_emux_note_off`, `snd_emux_key_press`, `snd_emux_update_channel`, `snd_emux_update_port`, `snd_emux_control`, `snd_emux_terminate_note`, `snd_emux_terminate_all`, `snd_emux_sounds_off_all`, `snd_emux_init_voices`, `snd_emux_lock_voice`, and `snd_emux_unlock_voice`. Internal helpers include `get_zone`, `get_bank`, `exclusive_note_off`, `terminate_voice`, `update_voice`, `setup_voice`, `calc_pan`, `calc_volume`, and `calc_pitch`.

## Control flow
Note-on resolves the active bank/preset, searches soundfont zones for note/velocity, applies exclusive-class note-off for drums, allocates one hardware voice per matching zone through `emu->ops.get_voice`, fills voice fields, copies and computes register state, optionally lets hardware prepare, then triggers all standby voices for that MIDI channel. Note-off marks matching voices released; if note-on and note-off occur in the same jiffy, release is deferred by a timer to avoid hardware artifacts. Key pressure and MIDI controls recalculate live voice volume, pitch, pan, or modulation and call hardware update callbacks.

Termination functions walk the voice table under `voice_lock`, call hardware terminate/free/reset callbacks, and clear voice ownership. `setup_voice` copies the soundfont zone, applies raw effects, computes current attenuation, pitch, pan/aux, filter target, pitch target, and volume target. Bank selection follows XG, GS, and default/drum conventions. Voice initialization marks all voices off and binds them to `emu` and hardware.

## State and persistence behavior
Voice state is held in `emu->voices`: state, time ordering, MIDI channel, port, key/note/velocity, soundfont zone/sample block, copied register set, computed attenuation/pitch/pan/filter targets, and hardware identifiers. The global `use_time` counter drives allocation age and termination ordering. A timer persists pending same-jiffy note releases. No disk persistence exists.

## Dependencies and integration points
The engine depends on ALSA MIDI channel state, soundfont zone search and volume tables, EMUX hardware operation callbacks, raw effects, jiffies/timers, and sequencer event routing from `emux_seq.c`. Hardware drivers provide voice allocation, prepare, trigger, release, terminate, update, free/reset, and optional pitch shift.

## Risks and edge cases
Hardware callbacks are invoked under `voice_lock` in many paths, so callback locking must not recurse or sleep unexpectedly. Same-jiffy note-off deferral prevents one artifact but adds timer ordering complexity. `snd_emux_update_channel` updates all voices with a matching channel pointer regardless of state before `update_voice` filters. Soundfont zones without samples produce voices with null blocks and depend on hardware prepare handling. Volume/pitch calculations use many lookup tables and clamps; regressions are audible rather than compile-visible.

## Test signals
Test note-on/off for melodic and drum banks, multi-zone layered presets, exclusive drum classes, immediate note-off deferral, pitchbend/RPN tuning, pan modes, expression/master volume, key pressure, all-notes/sounds-off, voice lock/unlock, hardware callback ordering, and stress with max voices exhausted.
