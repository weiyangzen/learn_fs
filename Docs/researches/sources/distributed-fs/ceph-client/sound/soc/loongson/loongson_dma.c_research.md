# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_dma.c

## Purpose
Provides a custom PCM DMA component for Loongson PCI I2S, programming ring descriptors directly through Loongson DMA order registers instead of using generic dmaengine.

## Important APIs, Types, And Functions
`struct loongson_dma_desc` models hardware descriptors. `struct loongson_runtime_data` owns coherent descriptor arrays and a position descriptor. Component ops implement `open`, `close`, `hw_params`, `trigger`, `pointer`, `mmap`, and `pcm_new`. `dma_desc_save()` asks hardware to copy current descriptor state into the position descriptor. `loongson_pcm_dma_irq()` reports periods elapsed.

## Control Flow, State, And Persistence
Open applies 128-byte period/buffer alignment, allocates a descriptor page and a position descriptor, and stores CPU DAI DMA data. `hw_params` validates period division, populates a circular descriptor chain, and sets runtime buffer metadata. Trigger writes the current descriptor address plus start/stop control bits into the order register and busy-waits for start clear. Pointer asks hardware to save descriptor state and calculates frames from current source address.

## Dependencies And Integration Points
Depends on `loongson_i2s.h` DMA data, PCI front-end-provided order registers and IRQs, coherent DMA allocation, fixed PCM buffers, and ASoC component registration by `loongson_i2s_pci.c`.

## Risks And Test Signals
Risks include busy waits without timeout in DMA order operations, descriptor count limited to one page, pointer math assuming source address tracks memory position, manual mmap with `remap_pfn_range()`, and IRQ request per PCM stream. Test signals include PCI playback/capture interrupts, 64-bit and 32-bit DMA masks, pause/resume, pointer wrap, period sizes at alignment limits, and xrun behavior.
