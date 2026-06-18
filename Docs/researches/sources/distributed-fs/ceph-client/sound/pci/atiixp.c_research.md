# sources/distributed-fs/ceph-client/sound/pci/atiixp.c

## Purpose
This file is the ALSA PCI driver for ATI IXP AC97 audio controllers, covering analog playback/capture, optional S/PDIF, AC97 codec control, DMA rings, interrupts, power management, and proc register dumps.

## Important APIs, Types, And Functions
Core state is `struct atiixp`, with per-stream `struct atiixp_dma`, descriptor `struct atiixp_dma_desc`, and per-DMA `struct atiixp_dma_ops`. Important functions include `snd_atiixp_init()`, `__snd_atiixp_probe()`, `snd_atiixp_aclink_reset()`, codec read/write helpers, `atiixp_build_dma_packets()`, PCM open/close/hw_params/trigger/pointer callbacks, `snd_atiixp_interrupt()`, mixer/PCM creation, and suspend/resume handlers.

## Control Flow
Probe creates an ALSA card, maps MMIO BAR0, requests IRQ, resets AC-link, detects codecs through not-ready interrupts, builds AC97 mixers, creates analog and digital PCM devices, starts the chip, and registers the card. PCM hw_params allocates a coherent descriptor ring and links period descriptors in a loop. Trigger callbacks enable or disable DMA transfer bits under `reg_lock`, flush FIFOs on stop, and maintain running/suspended state. IRQs report period elapsed or xrun per DMA and collect codec-detection bits. Resume resets AC-link, restarts the chip, resumes codecs, and restores descriptors for suspended streams.

## State, Persistence, And Dependencies
State persists in `struct atiixp`: MMIO base, IRQ, AC97 bus/codecs, PCM devices, descriptor buffers, DMA flags, codec detection bits, max channel count, S/PDIF mode, and mutex/spinlock state. Dependencies include ALSA core/PCM/AC97/info APIs, Linux PCI/MMIO/IRQ/PM, and module parameters for index, id, AC97 clock, quirks, codec override, and S/PDIF transport.

## Integration Points
The driver registers as a PCI module for SB200/SB300/SB400/SB600 AC97 IDs and exposes ALSA PCM, mixer, chmap, and proc interfaces.

## Risks
Descriptor and buffer DMA addresses are cast to `u32`, requiring effective 32-bit DMA addressing. Codec detection relies on interrupts and timing. SPDIF over AC-link shares playback DMA and is serialized with `open_mutex`. Partial or invalid DMA pointer reads return zero, which can cause audible artifacts. Some known codec rates are forced to 48 kHz due hardware limitations.

## Test Signals
Signals include successful probe on each PCI ID, AC97 codec detection with and without quirks, analog 2/4/6/8 channel playback, capture, S/PDIF AC-link and direct modes, xrun recovery, suspend/resume with active streams, proc register output, and clean card removal through devm resources.
