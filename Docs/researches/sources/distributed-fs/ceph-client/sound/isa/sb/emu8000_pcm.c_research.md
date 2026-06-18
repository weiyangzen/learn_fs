# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_pcm.c

## Purpose
`emu8000_pcm.c` exposes an ALSA playback-only PCM device that uses EMU8000 sample DRAM and wavetable voices as a PCM playback engine. It allocates DRAM buffers, writes PCM samples into card memory, sets up one or two voices, starts/stops playback, and uses a software timer to report periods.

## Important APIs, Types, and Functions
- `struct snd_emu8k_pcm` stores the EMU8000 pointer, substream, memory block, offsets, buffer/period sizes, loop starts, pitch, panning, playback pointer state, voice count, DRAM/timer/running flags, and timer lock.
- PCM ops: `emu8k_pcm_open`, `emu8k_pcm_close`, `emu8k_pcm_hw_params`, `emu8k_pcm_hw_free`, `emu8k_pcm_prepare`, `emu8k_pcm_trigger`, `emu8k_pcm_pointer`, `emu8k_pcm_copy`, and `emu8k_pcm_silence`.
- DRAM helpers: `emu8k_open_dram_for_pcm`, `emu8k_close_dram`, `snd_emu8000_write_wait`, `setup_voice`, `start_voice`, and `stop_voice`.
- Public creator: `snd_emu8000_pcm_new`.

## Control Flow
Open allocates per-substream state and constrains period time to timer granularity. `hw_params` allocates a card DRAM block large enough for audio plus blank loop padding. `prepare` computes pitch from sample rate, loop starts, channel panning, opens DRAM for PCM if needed, clears blank regions, and programs voices. Copy/silence writes frames into EMU8000 DRAM through SMALW/SMARW/SMLD/SMRD. Trigger start starts each voice and a one-jiffy timer; the timer reads current address from CCCA, computes pointer deltas and period transitions, then calls `snd_pcm_period_elapsed`. Trigger stop stops voices and deletes the timer.

## State and Persistence
State is per-open runtime state in `struct snd_emu8k_pcm` and a memory block from `emu->memhdr`. DRAM contents persist while the PCM buffer is allocated. No disk persistence exists.

## Dependencies and Integration Points
It depends on `emu8000_local.h`, ALSA PCM APIs, EMU8000 register helpers, emux voice locking, and the memory header created by `emu8000_synth.c`. It is created only when EMU8000 DRAM is available.

## Risks and Test Signals
Risks include timer-based period accounting drift, voice lock/unlock balance, memory block cleanup when DRAM was opened, signal interruption returning `-EAGAIN` during copy/silence, and stereo interleaving through separate left/right write ports. Test signals include mono/stereo playback, continuous sample-rate pitch calculation, large buffer/period combinations, start/stop races, hw_params reallocation, silence fill, pointer wrap, and module removal while PCM exists.
