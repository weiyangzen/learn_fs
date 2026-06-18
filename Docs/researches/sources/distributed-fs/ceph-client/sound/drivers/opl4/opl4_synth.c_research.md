# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_synth.c

## Purpose
Implements OPL4 wavetable MIDI synthesis: voice allocation, tone selection from YRW801 regions, volume/pan/pitch/vibrato calculations, register programming, note on/off, controllers, and GS master volume sysex handling.

## Important APIs, Types, And Functions
Exports `snd_opl4_synth_reset()`, `snd_opl4_synth_shutdown()`, `snd_opl4_note_on()`, `snd_opl4_note_off()`, `snd_opl4_terminate_note()`, `snd_opl4_control()`, and `snd_opl4_sysex()`. Important helpers include `snd_opl4_update_volume()`, `snd_opl4_update_pan()`, `snd_opl4_update_vibrato_depth()`, `snd_opl4_update_pitch()`, `snd_opl4_get_voice()`, and `snd_opl4_wait_for_wave_headers()`.

## Control Flow
Reset damps all 24 voices, initializes off/on voice lists, and clears MIDI channels. Note-on selects program or drum region, finds up to two matching key regions, steals from the oldest off voice or oldest on voice, writes tone number registers to trigger header load, sets pan/pitch/initial level while loading, waits for header completion, writes envelope/LFO/tremolo parameters, then sets key-on. Note-off clears key-on and moves voices to the off list; terminate also sets damp. Controllers update active voices by channel for modwheel/vibrato depth, main volume, pan, expression, and pitch bend. Parsed GS master volume sysex updates all active voice volumes.

## State And Persistence
Voice state is held in `opl4->voices[]`, `off_voices`, `on_voices`, each voice's channel/note/velocity/sound pointers, cached register fields, and MIDI channel data. The YRW801 region table is static read-only data.

## Dependencies And Integration
Depends on OPL4 register helpers, YRW801 regions, ALSA MIDI channel semantics, `volume_boost` from `opl4_seq.c`, and OPL4 register constants from `opl4_local.h`.

## Risks And Test Signals
Voice stealing can cut active notes under high polyphony. No voice is played if a note has no matching region; no explicit error is reported. Pitch and volume math clamp values but depends on static lookup tables. Tests should cover melodic and drum programs, two-region layered sounds, voice exhaustion, controllers on active notes, pitch bend and tuning, sysex master volume, and shutdown/reset muting.
