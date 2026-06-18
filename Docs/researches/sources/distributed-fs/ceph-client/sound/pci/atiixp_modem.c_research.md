# sources/distributed-fs/ceph-client/sound/pci/atiixp_modem.c

## Purpose
This file is the ALSA PCI driver for ATI IXP MC97 modem controllers, exposing modem-class playback and capture over AC97 modem codecs.

## Important APIs, Types, And Functions
It mirrors the audio driver with `struct atiixp_modem`, `struct atiixp_dma`, `struct atiixp_dma_desc`, and `struct atiixp_dma_ops`. Key functions include AC97 codec access, AC-link reset/down, codec detection, chip start/stop, descriptor ring build/clear, PCM callbacks, IRQ handler, mixer creation, PM handlers, proc dump setup, and PCI probe.

## Control Flow
Probe creates a card, enables PCI/MMIO/IRQ, resets the AC-link, detects modem codecs, creates an AC97 bus with `AC97_SCAP_SKIP_AUDIO`, registers one modem-class PCM device, starts interrupts, and registers the card. PCM open applies modem rate constraints of 8000, 9600, 12000, and 16000 Hz, enables DMA, and records the stream. hw_params builds the descriptor ring and programs modem codec line rate and level. Trigger toggles modem send/receive bits and flushes FIFOs on stop. IRQ handles playback/capture period and xrun events plus codec-detection interrupts.

## State, Persistence, And Dependencies
Persistent state includes MMIO/IRQ data, AC97 modem codecs, descriptor buffers, PCM devices, codec-not-ready bits, and open serialization. Dependencies are ALSA PCM/AC97/core/info APIs, Linux PCI/MMIO/IRQ/PM, and module parameters for index, id, and AC97 clock.

## Integration Points
The PCI table binds SB200 and SB400 modem controller IDs. ALSA sees a modem PCM device named `ATI IXP MC97`, and `/proc/asound` can expose the `atiixp-modem` register dump.

## Risks
Much code is duplicated from `atiixp.c`, so fixes can diverge. DMA addresses are narrowed to `u32`. GPIO writes special-case `AC97_GPIO_STATUS`, so normal codec write assumptions do not always apply. Resume does not rebuild active DMA descriptors like the audio driver does. Codec detection depends on interrupt timing.

## Test Signals
Test signals include modem PCI probe, AC97 modem codec creation, constrained-rate playback and capture, GPIO status writes, xrun and period IRQs, suspend/resume, proc register dump, and clean behavior when no modem codec is detected.
