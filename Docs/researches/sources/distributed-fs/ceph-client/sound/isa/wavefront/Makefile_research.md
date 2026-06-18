# sources/distributed-fs/ceph-client/sound/isa/wavefront/Makefile

## Purpose
This Makefile defines the ALSA WaveFront module composition for Turtle Beach Maui/Tropez/Tropez+ support.

## Important APIs, Types, and Functions
It sets `snd-wavefront-y := wavefront.o wavefront_fx.o wavefront_synth.o wavefront_midi.o`, meaning those four objects are linked into one module. It adds `snd-wavefront.o` to the build when `CONFIG_SND_WAVEFRONT` is enabled.

## Control Flow
There is no runtime control flow. Build-time flow is Kbuild object aggregation: the module entry points are in `wavefront.c`, while FX, synth, and MIDI support are linked into the same object.

## State and Persistence
No runtime state. Build state is controlled by `CONFIG_SND_WAVEFRONT`.

## Dependencies and Integration Points
The file integrates this directory with the parent ALSA ISA Kbuild. It requires all four object files to compile cleanly because they become a single module.

## Risks and Edge Cases
Adding or removing WaveFront support files requires updating this list. Since `wavefront_synth.o` is linked but not part of this work item, behavior referenced by `wavefront.c` depends on that sibling object.

## Test Signals
With `CONFIG_SND_WAVEFRONT=m`, Kbuild should produce `snd-wavefront.ko` containing symbols from card, FX, synth, and MIDI implementation files.
