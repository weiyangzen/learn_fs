# sources/distributed-fs/ceph-client/sound/ppc/snd_ps3.h

## Purpose

This header defines the PS3 sound driver's private data structures, enums, constants, DMA sizing, and driver name.

## Important APIs, types, and functions

Enums identify output channels, DMA fill modes, and left/right channels. `struct snd_ps3_avsetting_info` caches PS3AV audio channel/rate/width/format/source and IEC958 channel-status bytes. `struct snd_ps3_card_info` stores system-bus device, ALSA card/PCM/substream, MMIO, IRQ outlet/number, AV settings, DMA ring pointers, running/silent state, null buffer, and startup delay. Constants define FIFO stage/count/size, DMA block size, preallocation, DMA region size, and audio IOID.

## Control flow

There is no executable logic. The enum values drive control flow in `snd_ps3_program_dma()` and interrupt handling by distinguishing first-fill/running and silent/non-silent programming.

## State and persistence behavior

This header specifies the persistent global state held by `snd_ps3.c`. The left and right DMA rings are represented as separate pointer sets into a split noninterleaved ALSA buffer.

## Dependencies and integration points

It depends on Linux IRQ types and constants from `snd_ps3_reg.h` for DMA size expressions. It is private to the PS3 sound driver.

## Risks and test signals

Risks include constants drifting from hardware register definitions, insufficient preallocation for supported periods, and state fields not covered by locking. Test with compile checks, runtime period constraints, pointer reporting, and lockdep around `dma_lock`.
