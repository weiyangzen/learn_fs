# sources/distributed-fs/ceph-client/sound/isa/sb/sb8_main.c

## Purpose
This file implements the low-level PCM engine and interrupt handling for 8-bit Sound Blaster, Sound Blaster Pro, and Jazz16-like cards. It handles legacy DSP command programming, ISA DMA, SB Pro stereo constraints, and half-duplex ALSA PCM registration.

## Important APIs, Types, and Functions
The exported APIs are `snd_sb8dsp_pcm()` and `snd_sb8dsp_interrupt()`, with MIDI exports declared for companion `sb8_midi.c`. PCM operations include `snd_sb8_open()`, `snd_sb8_close()`, playback/capture prepare and trigger functions, and pointer callbacks. Rate constraints use `clock`, `hw_constraints_clock`, `stereo_clocks`, `snd_sb8_hw_constraint_rate_channels()`, and `snd_sb8_hw_constraint_channels_rate()`.

## Control Flow
Open is half-duplex: it rejects any already open PCM stream, records playback or capture substream, assigns base hardware constraints, then adjusts constraints by hardware type. SB Pro allows stereo only at particular timer-derived rates, Jazz16 permits wider rates and optional 16-bit samples when DMA16 is valid, and later DMA configurations loosen buffer size limits.

Playback prepare chooses the DSP command family based on hardware and rate, handles SB Pro stereo by enabling mixer stereo, forcing a dummy interrupt sequence, setting the sample-rate divisor, optionally disabling playback filter, setting the block size, and programming ISA DMA in autoinit write mode. Capture prepare similarly selects input command mode, disables speaker, sets stereo/sample-rate/filter state, programs block size, and programs DMA read mode. Triggers start the stored DSP command; single-cycle SB1 commands write a count every start. Stops disable DMA or reset DSP for high-speed modes and restore stereo/filter state.

The interrupt handler acknowledges the 8-bit DSP interrupt, switches on `chip->mode`, retriggers non-autoinit SB1-style transfers when needed, and calls `snd_pcm_period_elapsed()` for the active substream.

## State and Persistence
State is held in `struct snd_sb`: mode bits, playback/capture format commands, period and buffer sizes, substream pointers, DMA numbers, and temporary use of `force_mode16` to stash old SB Pro mixer filter/stereo register values. No persistent storage is used.

## Dependencies and Integration Points
The code depends on SB command and ack helpers, SB mixer helpers, ALSA PCM runtime constraints, and ISA DMA helpers. It is invoked by `sb8.c` after `snd_sbdsp_create()` detects a compatible DSP.

## Risks and Edge Cases
The code documents lack of access to old SB8 hardware and contains timing-sensitive paths. Stereo setup uses a forced interrupt and temporary mixer/filter state. `force_mode16` is repurposed for SB Pro filter state, so future changes must avoid assuming it only means 16-bit DMA allocation in SB8 contexts. Some trigger switch statements do not reject unknown commands explicitly.

## Test Signals
Confirm mono playback/capture on SB1/SB2, SB Pro stereo only at legal rates, Jazz16 16-bit mode when DMA16 is 5 or 7, period interrupts in both autoinit and single-cycle modes, correct DMA pointer reporting, and mixer filter/stereo restoration after stop.
