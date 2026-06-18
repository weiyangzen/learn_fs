# sources/distributed-fs/ceph-client/sound/isa/sb/Makefile

## Purpose
This Makefile builds ALSA ISA Sound Blaster-family modules, including common SB support, SB8/SB16 DSP modules, SB/AWE cards, EMU8000 sequencer synth support, Jazz16, and optional SB16 CSP composition.

## Important APIs, Types, and Functions
There are no runtime APIs. Build variables compose modules: `snd-sbawe-y := sbawe.o emu8000.o`, `snd-emu8000-synth-y := emu8000_synth.o emu8000_callback.o emu8000_patch.o emu8000_pcm.o`, and `snd-jazz16-y := jazz16.o`. Config symbols add modules to `obj-*`.

## Control Flow
Kbuild includes object lists according to `CONFIG_SND_*`. If `CONFIG_SND_SB16_CSP=y`, the CSP object is linked into both SB16 and SBAWE modules. `CONFIG_SND_SBAWE_SEQ` controls the EMU8000 synth plugin module.

## State and Persistence
No runtime state exists. Build configuration controls module contents.

## Dependencies and Integration Points
It integrates `emu8000.c` into the AWE card driver and the separate sequencer synth plugin with callback, patch, and PCM support objects.

## Risks and Test Signals
Risks include missing EMU8000 companion objects or incorrect CSP linkage under built-in/module combinations. Test signals include successful builds for SB common, SB8/SB16, SBAWE, SBAWE sequencer, and Jazz16 config combinations.
