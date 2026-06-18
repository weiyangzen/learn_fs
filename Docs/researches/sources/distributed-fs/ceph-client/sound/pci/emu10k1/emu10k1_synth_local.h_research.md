# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_synth_local.h

## Purpose

`emu10k1_synth_local.h` is the private header shared by the EMU10K1 wavetable synth module files. It declares patch, memory-header, callback setup, and voice-stealing interfaces.

## Important APIs, Types, and Functions

The header includes `sound/core.h` and `sound/emu10k1_synth.h`, then declares `snd_emu10k1_sample_new()`, `snd_emu10k1_sample_free()`, `snd_emu10k1_memhdr_init()`, `snd_emu10k1_ops_setup()`, and `snd_emu10k1_synth_get_voice()`.

## Control Flow

`emu10k1_synth.c` includes this header to call `snd_emu10k1_ops_setup()`. `emu10k1_callback.c` includes it to expose callback setup and use sample callbacks. `emu10k1_patch.c` includes it to define the sample allocation/free functions declared here.

## State and Persistence Behavior

The header owns no state, but its prototypes define how synth files manipulate persistent emux state, EMU10K1 sample memory blocks, and hardware voice allocation.

## Dependencies and Integration Points

It is a local integration point between the synth registration, callback, and patch-transfer files, and with public ALSA EMU10K1 synth structures.

## Risks and Test Signals

Risks are prototype drift or exposing functions with mismatched types across synth files. Test signals are successful build of `snd-emu10k1-synth`, clean modpost, and runtime synth probe with patch loading and voice callbacks.
