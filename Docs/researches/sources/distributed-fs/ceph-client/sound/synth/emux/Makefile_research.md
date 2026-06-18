# sources/distributed-fs/ceph-client/sound/synth/emux/Makefile

## Purpose
This Kbuild file defines the `snd-emux-synth` module, the shared ALSA EMU wavetable synthesizer implementation.

## Important APIs, types, and functions
`snd-emux-synth-y` includes `emux.o`, `emux_synth.o`, `emux_seq.o`, `emux_nrpn.o`, `emux_effect.o`, `emux_hwdep.o`, and `soundfont.o`. `snd-emux-synth-$(CONFIG_SND_PROC_FS)` optionally adds `emux_proc.o`. A conditional adds `emux_oss.o` when `CONFIG_SND_SEQUENCER_OSS` is nonempty. `obj-$(CONFIG_SND_SYNTH_EMUX)` controls final linkage.

## Control flow
There is no runtime flow. Kbuild selects which support files contribute to the module based on procfs and OSS sequencer options.

## State and persistence behavior
Only static build graph state is encoded.

## Dependencies and integration points
It integrates the EMUX core, synth voice logic, sequencer interface, NRPN/SYSEX handling, raw effects, hwdep patch loading, soundfont logic, optional proc diagnostics, and optional OSS compatibility into one module.

## Risks and edge cases
Changing feature guards can create unresolved symbols because prototypes in `emux_voice.h` depend on `CONFIG_SND_PROC_FS`, `CONFIG_SND_SEQUENCER_OSS`, and `SNDRV_EMUX_USE_RAW_EFFECT`. `emux_oss.o` is included by a nonempty test rather than `obj-*`, so the exact Kconfig string behavior matters.

## Test signals
Build combinations with procfs on/off and OSS sequencer on/off should confirm the expected object set and symbol closure.
