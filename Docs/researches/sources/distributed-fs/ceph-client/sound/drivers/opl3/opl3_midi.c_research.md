# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_midi.c

## Purpose
Converts ALSA MIDI channel events into OPL2/OPL3 FM register programming for the sequencer and OSS synth paths. It handles voice allocation, patch lookup, pitch/volume math, note lifecycle, and controller effects.

## Important APIs, Types, And Functions
Public MIDI callbacks are `snd_opl3_note_on()`, `snd_opl3_note_off()`, `snd_opl3_key_press()`, `snd_opl3_terminate_note()`, `snd_opl3_control()`, `snd_opl3_nrpn()`, and `snd_opl3_sysex()`. Shared helpers include `snd_opl3_calc_volume()` and `snd_opl3_timer_func()`. The file also contains logarithmic volume and pitch tables, `opl3_get_voice()`, `snd_opl3_kill_voice()`, and pitch update helpers.

## Control Flow
For note-on, the code chooses bank/program from sequencer mode, drum status, or OSS mode, finds a loaded patch, determines 2-op versus 4-op capability, allocates a voice, clears any previous key-on state, sets the OPL3 4-op connection register if needed, writes operator registers, computes f-number/block, keys the voice on, schedules fixed-duration note-off if requested, and records voice bookkeeping. Note-off scans voices matching channel/note in sequencer mode or remaps the OSS voice and clears key-on. Controller events update vibrato/tremolo depth or recompute pitch bend.

## State And Persistence
State is in `opl3->voices[]`, `use_time`, `connection_reg`, `drum_reg`, system timer fields, channel state, and loaded patches managed elsewhere. It is runtime-only and reset during synth setup/cleanup.

## Dependencies And Integration
Depends on `opl3_synth.c` patch storage, `opl3_drums.c` for internal percussion, ALSA MIDI channel processing, and the low-level `opl3->command()` callback.

## Risks And Test Signals
Voice stealing is heuristic and must avoid corrupting paired 4-op voices. Extra-program recursion is intentionally limited but still complicates note-off grouping. Fixed-duration notes depend on jiffies equality in the timer callback, which is timing-sensitive. Test signals include 2-op/4-op patches, pitch bend, pan, volume/expression, percussion, extra program patches, OSS voice remapping, and voice exhaustion.
