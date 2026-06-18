# sources/distributed-fs/ceph-client/include/sound/emu10k1_synth.h

## Purpose
This header defines the sequencer device ID and argument block used to bind EMU10K1 hardware to the generic emux wavetable synth layer.

## Important APIs, Types, and Constants
It includes `sound/emu10k1.h` and `sound/emux_synth.h`, defines `SNDRV_SEQ_DEV_ID_EMU10K1_SYNTH`, `EMU10K1_MAX_MEMSIZE`, and `struct snd_emu10k1_synth_arg` containing the EMU chip pointer, sequence ports, maximum voices, and index.

## Control Flow
The EMU10K1 driver passes this argument block when registering a sequencer synth device. The emux layer then calls back into EMU10K1-specific allocation and voice programming routines.

## State and Persistence
The argument struct is setup-time glue. Persistent synth state lives in `struct snd_emu10k1`, emux structures, and allocated sample memory.

## Dependencies and Integration Points
It directly bridges EMU10K1 core driver internals with the ALSA sequencer/emux synth subsystem.

## Risks and Edge Cases
`max_voices` and `seq_ports` must not exceed hardware/emux limits. `EMU10K1_MAX_MEMSIZE` constrains sample memory exposure; mismatches with actual card memory handling can fail sample loading.

## Test Signals
Sequencer device registration, soundfont loading up to memory limits, MIDI note playback, voice exhaustion, and unregister paths validate the interface.
