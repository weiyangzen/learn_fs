# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_dma.h

## Purpose
Declares the Loongson PCI I2S custom PCM component shared between the PCI front end and DMA implementation.

## Important APIs, Types, And Functions
The header includes ASoC and declares `extern const struct snd_soc_component_driver loongson_i2s_component`.

## Control Flow, State, And Persistence
No control flow or state exists in the header.

## Dependencies And Integration Points
Included by `loongson_i2s_pci.c` to register the component implemented in `loongson_dma.c`.

## Risks And Test Signals
Risks are declaration/definition drift and name collision with the platform front-end component driver. Test signals are PCI I2S builds and successful component registration.
