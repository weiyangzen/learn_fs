# sources/distributed-fs/ceph-client/sound/soc/au1x/dma.c

## Purpose
ASoC PCM component for older Au1000/Au1500/Au1100 audio using the legacy Alchemy DMA controller. It builds a circular software list of PCM periods, programs double-buffered DMA registers, handles DMA interrupts, and reports ALSA PCM position.

## Important APIs, Types, And Functions
- `struct pcm_period` describes a period start and end offset in a circular list.
- `struct audio_stream` stores substream, DMA channel, period list, and geometry.
- `au1000_setup_dma_link()` creates the circular period list from runtime DMA area.
- `au1000_dma_start/stop()` program and control DMA buffers.
- `au1000_dma_interrupt()` handles done flags, advances the list, reloads buffer addresses, and notifies ALSA.
- Component ops are `alchemy_pcm_open/close/hw_params/hw_free/trigger/pointer/pcm_new`.

## Control Flow
Open obtains DMA IDs from the CPU DAI, requests the Alchemy DMA channel, disables noncoherent mode, stores the substream, and sets hardware constraints. `hw_params` builds the circular period list. Trigger start initializes and starts double-buffered DMA; stop disables DMA. IRQ moves to the next period, reloads the completed DMA buffer, and calls `snd_pcm_period_elapsed`. Close frees the DMA channel.

## State And Persistence
Per-stream state lives in `struct alchemy_pcm_ctx` allocated at probe. Period nodes are heap-allocated on `hw_params` and freed on `hw_free`; DMA channel state is held while stream is open.

## Dependencies And Integration Points
Depends on legacy `au1000_dma.h` APIs, CPU DAIs that supply DMA request IDs, and continuous managed PCM buffers.

## Risks
Uses `virt_to_phys(runtime->dma_area)` rather than DMA mapping helpers, matching old contiguous-buffer assumptions. Pointer math depends on current period and DMA residue. The `case (~DMA_D0 & ~DMA_D1)` expression is suspicious as an empty-IRQ case and may not express intended flag matching. Memory allocation per period can fail for high period counts.

## Test Signals
Open/close DMA allocation, playback/capture period interrupts, pointer wrap, missed-interrupt branch, hw_params reconfiguration, and DMA residue correctness.
