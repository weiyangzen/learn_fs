# sources/distributed-fs/ceph-client/sound/soc/au1x/dbdma2.c

## Purpose
ASoC PCM platform component for Au12x0/Au1550 PSC audio using Alchemy descriptor-based DMA. It manages DMA channel allocation, descriptor queueing, period callbacks, PCM pointer reporting, and managed DMA buffers.

## Important APIs, Types, And Functions
- `struct au1xpsc_audio_dmadata` stores DDMA id/channel, substream, ring position, DMA buffer addresses, period geometry, and current bit width.
- `au1x_pcm_dbdma_realloc()` allocates or reallocates a two-descriptor ring when sample bit width changes.
- `au1x_pcm_queue_tx/rx()` queue the next period as source or destination.
- Component ops are open, close, hw_params, prepare, trigger, pointer, and pcm_new.

## Control Flow
Open retrieves DMA IDs from the CPU DAI and installs hardware constraints. `hw_params` reallocates the DDMA channel if needed and initializes period state. Prepare resets the DMA channel and prequeues two periods. Trigger starts or stops DDMA. DMA callbacks advance period counters, notify ALSA with `snd_pcm_period_elapsed`, and queue the next period. Close frees the DDMA channel.

## State And Persistence
Per-stream runtime state is allocated as two `au1xpsc_audio_dmadata` entries on probe. It is reset per `hw_params`/close. No persistent state beyond DMA channel allocation.

## Dependencies And Integration Points
Depends on Alchemy DBDMA APIs, ASoC component PCM ops, and CPU DAIs that provide playback/capture DBDMA IDs. Platform driver name is `au1xpsc-pcm`.

## Risks
The code assumes a two-descriptor ring and queues exactly two periods before start. Bit width changes force channel reallocation because the DBDMA API cannot adjust existing descriptor width. Pointer state is callback-driven and can drift if callbacks are missed. Buffer minimum is large to reduce skips.

## Test Signals
Playback/capture with different sample widths, period elapsed cadence, pointer monotonicity/wrap, close freeing DDMA, and underrun behavior with small period sizes.
