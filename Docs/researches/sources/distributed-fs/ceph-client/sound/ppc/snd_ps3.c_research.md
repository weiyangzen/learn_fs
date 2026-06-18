# sources/distributed-fs/ceph-client/sound/ppc/snd_ps3.c

## Purpose

This file implements the PlayStation 3 ALSA playback driver. It maps PS3 audio MMIO and DMA regions, programs the PS3 AV audio mode, manages a noninterleaved stereo DMA ring, handles audio FIFO interrupts, exposes IEC958 controls, and registers a PS3 system-bus sound driver.

## Important APIs, types, and functions

The single global `the_card` is `struct snd_ps3_card_info`. PCM ops include `snd_ps3_pcm_open()`, `close()`, `prepare()`, `trigger()`, and `pointer()`. DMA helpers include `snd_ps3_program_dma()`, `snd_ps3_kick_dma()`, `snd_ps3_wait_for_dma_stop()`, and `snd_ps3_verify_dma_stop()`. AV helpers include `snd_ps3_change_avsetting()`, `snd_ps3_set_avsetting()`, and `snd_ps3_init_avsetting()`. Platform lifecycle is handled by `snd_ps3_driver_probe()`, `snd_ps3_driver_remove()`, `snd_ps3_init()`, and `snd_ps3_exit()`.

## Control flow

Module init checks for PS3 LV1 firmware and registers a PS3 system-bus driver. Probe opens the hypervisor device, maps MMIO, creates a DMA region, sets a 32-bit DMA mask, programs audio base address, allocates IRQ, creates ALSA card/controls/PCM, allocates a null buffer, initializes AV settings with silent data, and registers the card. Playback prepare updates AV rate/width and ring pointers. Trigger start primes silent DMA, starts chained DMA requests, and interrupt handling refills four FIFO stages per empty event, using silent fill for startup delay or underflow recovery before reporting periods.

## State and persistence behavior

All runtime state is global in `the_card`: mapped MMIO, IRQ, AV settings, PCM/substream pointers, DMA ring start/next/last pointers for left and right halves, buffer size, running flag, silent countdown, null buffer, and start delay. `dma_lock` protects ring pointers and running transitions.

## Dependencies and integration points

It depends on PS3 LV1 calls, PS3 system bus, PS3 AV APIs, ALSA PCM/control/memalloc, coherent DMA, and register definitions in `snd_ps3_reg.h`. It exposes a single SPDIF playback PCM with IEC958 controls backed by `ps3av_mode_cs_info`.

## Risks and test signals

Risks include global singleton assumptions, DMA address truncation to 32 bits, underflow recovery latency, silent delay period accounting, IRQ cleanup ordering, incomplete trigger command validation, and synchronization between interrupt and stop. Test module probe/remove, rates 44.1/48/88.2/96 kHz, 16/24-bit BE formats, IEC958 default changes, underflow recovery, stop while IRQs fire, and startup delay behavior.
