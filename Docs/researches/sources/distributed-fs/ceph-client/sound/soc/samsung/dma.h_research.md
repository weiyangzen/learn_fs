# sources/distributed-fs/ceph-client/sound/soc/samsung/dma.h

## Purpose
Declares Samsung's ASoC dmaengine registration helper for controller drivers that need a compatible DMA PCM platform with optional custom channel names and DMA device.

## Important APIs, Types, And Functions
Exports the prototype `samsung_asoc_dma_platform_register(struct device *dev, dma_filter_fn filter, const char *tx, const char *rx, struct device *dma_dev)`.

## Control Flow
No executable flow. Callers use the helper during probe after filling their `snd_dmaengine_dai_dma_data`.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `<sound/dmaengine_pcm.h>` and is used by Samsung I2S, PCM, and S/PDIF drivers. The comments document that `tx`/`rx` may be NULL when DMA channel names are the defaults.

## Risks And Edge Cases
The header does not encode ownership or lifetime; callers rely on the implementation's devm allocation.

## Test Signals
Build coverage and successful probe of all callers with default and explicit channel names.
