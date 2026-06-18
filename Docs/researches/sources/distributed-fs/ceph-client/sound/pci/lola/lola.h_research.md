# sources/distributed-fs/ceph-client/sound/pci/lola/lola.h

## Purpose
This header defines the Digigram Lola driver’s register map, protocol constants, shared state structures, MMIO helper macros, codec verbs, widget parameter helpers, and cross-file function prototypes.

## Important APIs, Types, and Functions
BAR0 constants model HD-audio global, CORB/RIRB, immediate command, and stream descriptor registers. BAR1 constants model Digigram-specific FPGA, stream, interrupt, board, mixer, peak-meter, and DSD registers. Core structs include `lola_bar`, `lola_rb`, `lola_pin`, `lola_pin_array`, `lola_sample_clock`, `lola_clock_widget`, `lola_mixer_array`, `lola_mixer_widget`, `lola_stream`, `lola_pcm`, and the top-level `struct lola`. Helper macros such as `lola_readl()`, `lola_writel()`, and `lola_dsd_read/write()` centralize MMIO addressing. Prototypes expose codec, PCM, clock, mixer, and proc functions.

## Control Flow
The header itself has no runtime flow, but it establishes the initialization order used by `lola.c`: detect stream counts into `pcm[]`, initialize audio widgets into `lola_stream`, pins into `pin[]`, clock metadata into `clock`, mixer register/shadow metadata into `mixer`, then create user-facing ALSA interfaces.

## State and Persistence
The state model is explicit in `struct lola`: BAR mappings, IRQ number, register lock/open mutex, CORB/RIRB queues, last command/debug response, stream arrays, SRC mask, pins, clock selection/frequency/validity, mixer matrix, hardware caps, module parameters, and flags. State persists only for the driver lifetime and may be replayed into hardware after reset.

## Dependencies and Integration Points
The header depends on ALSA PCM constants for `PLAY` and `CAPT`, Linux MMIO accessors through source users, and the Lola-specific codec verb protocol. It is included by every Lola implementation file and is the main internal ABI for the module.

## Risks
Many macros directly compute MMIO offsets; wrong BAR selection or DSD index can write to unrelated hardware registers. Fixed maxima (`MAX_STREAM_COUNT`, `MAX_PINS`, `LOLA_MIXER_DIM`, `MAX_SAMPLE_CLOCK_COUNT`) protect stack/static arrays but require validation against hardware values. `struct lola_mixer_array` overlays an MMIO region and must match hardware layout exactly.

## Test Signals
Compile coverage is important because this header carries prototypes and composite state. Runtime test signals include correct BAR register dumps in debug proc, stream counts bounded by header maxima, clock/mixer/pin parsing matching hardware variants, and absence of out-of-range stream DSD accesses during multi-channel playback/capture.
