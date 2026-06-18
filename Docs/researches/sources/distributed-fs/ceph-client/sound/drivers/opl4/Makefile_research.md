# sources/distributed-fs/ceph-client/sound/drivers/opl4/Makefile

## Purpose
Defines Kbuild objects for the ALSA OPL4 wavetable driver, split into a common device/mixer/proc library and an optional sequencer synth module with static YRW801 instrument data.

## Important APIs, Types, And Functions
`snd-opl4-lib-y` includes `opl4_lib.o` and `opl4_mixer.o`, with `opl4_proc.o` conditional on `CONFIG_SND_PROC_FS`. `snd-opl4-synth-y` includes `opl4_seq.o`, `opl4_synth.o`, and `yrw801.o`.

## Control Flow
`CONFIG_SND_OPL4_LIB` builds `snd-opl4-lib.o`; `CONFIG_SND_OPL4_LIB_SEQ` builds the sequencer synth object. The OPL4 library also causes the OPL3 library to be built via the OPL3 Makefile.

## State And Persistence
The file is declarative build state only.

## Dependencies And Integration
Integrates OPL4 with ALSA procfs, sequencer support, and the OPL3 FM core. The object split mirrors runtime layering: low-level PCM/mixer/proc support separate from MIDI wavetable synthesis.

## Risks And Test Signals
Configuration-specific build failures are the main risk, especially procfs off and sequencer off combinations. Kconfig matrix builds are the relevant tests.
