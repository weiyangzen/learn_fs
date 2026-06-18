# sources/distributed-fs/ceph-client/sound/drivers/opl3/Makefile

## Purpose
Defines the kernel build composition for the ALSA OPL3 FM support modules. It separates the common OPL3 library from the optional sequencer synth layer and conditionally includes OSS sequencer emulation.

## Important APIs, Types, And Functions
The build targets are `snd-opl3-lib-y := opl3_lib.o opl3_synth.o` and `snd-opl3-synth-y := opl3_seq.o opl3_midi.o opl3_drums.o`, with `opl3_oss.o` appended when `CONFIG_SND_SEQUENCER_OSS` is enabled.

## Control Flow
Kbuild links `snd-opl3-lib.o` for both `CONFIG_SND_OPL3_LIB` and `CONFIG_SND_OPL4_LIB`, reflecting OPL4's reuse of the FM OPL3 core. `CONFIG_SND_OPL3_LIB_SEQ` builds the sequencer-facing synth module.

## State And Persistence
The file is declarative build metadata and has no runtime state.

## Dependencies And Integration
Integrates with ALSA Kconfig symbols for OPL3, OPL4, sequencer, and OSS emulation. The OPL4 dependency on `snd-opl3-lib.o` is an important cross-folder integration point.

## Risks And Test Signals
Misconfigured object grouping would break symbol availability for drivers that create OPL3 or OPL4 devices. Build tests across `CONFIG_SND_OPL3_LIB`, `CONFIG_SND_OPL4_LIB`, `CONFIG_SND_OPL3_LIB_SEQ`, and `CONFIG_SND_SEQUENCER_OSS` are the primary signal.
