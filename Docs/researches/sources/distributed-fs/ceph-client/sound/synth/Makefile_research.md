# sources/distributed-fs/ceph-client/sound/synth/Makefile

## Purpose
This Kbuild file builds shared ALSA synthesizer support: utility memory management and the EMUX subdirectory.

## Important APIs, types, and functions
`snd-util-mem-y := util_mem.o` defines the shared memory helper module. `obj-$(CONFIG_SND_EMU10K1)`, `obj-$(CONFIG_SND_TRIDENT)`, and `obj-$(CONFIG_SND_SBAWE_SEQ)` add `snd-util-mem.o` for consumers. `obj-$(CONFIG_SND_SEQUENCER) += emux/` descends into the EMUX build when the ALSA sequencer is enabled.

## Control flow
There is no runtime flow. Kbuild emits helper objects and recurses into `emux/` based on configuration.

## State and persistence behavior
The file encodes static build dependencies only.

## Dependencies and integration points
It connects consumer sound drivers to `util_mem.o` and the EMUX layer. The EMUX subdirectory still gates its actual module on `CONFIG_SND_SYNTH_EMUX`.

## Risks and edge cases
Build skew is the main risk: new utility-memory consumers require another `obj-*` line, and EMUX source changes must stay coordinated with the subdirectory Makefile. Recursing into `emux/` when the sequencer is enabled does not by itself build EMUX unless `SND_SYNTH_EMUX` is set.

## Test signals
Build with EMU10K1, Trident, SBAWE, sequencer, and no-consumer combinations to confirm the expected objects and no duplicate or missing symbols.
