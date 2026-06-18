# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_drums.c

## Purpose
Implements the optional internal OPL2/OPL3 percussion mode used by the OPL3 sequencer synth when `use_internal_drums` is enabled. It maps GM drum notes to the five hardware percussion bits and programs fixed bass, hi-hat, snare, tom, and cymbal voices.

## Important APIs, Types, And Functions
`snd_opl3_drum_table` maps notes 35-81 to OPL3 percussion bit masks. `struct snd_opl3_drum_voice` and `struct snd_opl3_drum_note` describe fixed register settings. `snd_opl3_load_drums()` initializes the reserved percussion voices, and `snd_opl3_drum_switch()` turns a note on/off and updates per-hit volume/pan.

## Control Flow
Sequencer setup reserves voices 6-8, calls `snd_opl3_load_drums()`, enables percussion mode in `opl3->drum_reg`, and routes drum note-on/off events through `snd_opl3_drum_switch()`. On note-on, the code selects the relevant predescribed drum voice, adjusts level and stereo bits from MIDI velocity/pan, sets the percussion bit, and writes `OPL3_REG_PERCUSSION`. On note-off it clears that bit.

## State And Persistence
State lives in OPL3 hardware registers and `opl3->drum_reg`. There is no independent persistence; percussion setup is recreated on each synth subscription.

## Dependencies And Integration
Depends on `snd_opl3_regmap`, `snd_opl3_calc_volume()`, OPL3 register constants from `<sound/opl3.h>`, and the command callback stored in `struct snd_opl3`.

## Risks And Test Signals
The mapping compresses many GM notes onto five shared hardware percussion bits, so overlapping notes of the same hardware drum can cut each other off. Tests should cover notes below/above 35-81, velocity-to-level behavior, pan changes, percussion mode disabled, and interactions with melodic voices when internal drums reserve voices 6-8.
