# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_synth.c

## Purpose

`emu10k1_synth.c` registers the EMU10K1 wavetable synth as an ALSA sequencer device and connects the generic emux synth engine to EMU10K1 hardware callbacks.

## Important APIs, Types, and Functions

`snd_emu10k1_synth_probe()` reads `struct snd_emu10k1_synth_arg`, clamps max voices to 1..64, allocates an emux instance, installs EMU10K1 ops with `snd_emu10k1_ops_setup()`, wires hardware pointer, voice/port counts, sample memory header, MIDI port mapping, panning mode, and fixed hwdep index, then registers emux and stores it under `hw->synth`. `snd_emu10k1_synth_remove()` detaches `hw->synth` and `hw->get_synth_voice` under `voice_lock` and frees emux. `emu10k1_synth_driver` registers the sequencer driver for `SNDRV_SEQ_DEV_ID_EMU10K1_SYNTH`.

## Control Flow

The main PCI driver creates a sequence device with synth args during probe. The sequencer core calls this probe, which builds and registers emux. Removal reverses the hardware linkage before freeing emux to prevent callbacks into stale state.

## State and Persistence Behavior

State persists in the emux instance, `hw->synth`, and `hw->get_synth_voice`. The synth uses the main card's `memhdr`, so sample memory lifetime is tied to the hardware driver.

## Dependencies and Integration Points

It depends on ALSA sequencer/emux infrastructure, `emu10k1_synth_local.h`, and the main EMU10K1 card state provided through `snd_emu10k1_synth_arg`.

## Risks and Test Signals

Risks include invalid args, voice count outside hardware capacity, stale synth pointers on removal, and mismatched MIDI device indexes for Audigy versus non-Audigy. Test signals are sequencer synth device creation/removal, SoundFont load, MIDI playback through configured ports, and module unload with no dangling callbacks.
