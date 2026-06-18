# sources/distributed-fs/ceph-client/include/sound/dmaengine_pcm.h

## Purpose
This header exposes ALSA/ASoC helper APIs for implementing PCM devices backed by Linux DMAengine channels.

## Important APIs, Types, and Functions
Helpers include `snd_hwparams_to_dma_slave_config()`, `snd_dmaengine_pcm_trigger()`, open/close/sync-stop helpers, channel request/get helpers, config setup from DAI data, hwparams refinement, registration/unregistration, managed registration, and slave-config preparation. `snd_pcm_substream_to_dma_direction()` maps ALSA stream direction to DMA direction. `struct snd_dmaengine_dai_dma_data` describes addr, addr_width, maxburst, slave_id, filter_data, channel name, FIFO size, flags, peripheral config, and peripheral config length. `struct snd_dmaengine_pcm_config` provides callbacks, compatibility filters, channel names, PCM hardware, prealloc sizes, and flags. `struct dmaengine_pcm` embeds the ASoC component and per-stream channels.

## Control Flow
Drivers register a DMAengine PCM component for a device, provide DAI DMA metadata or config callbacks, open substreams to bind DMA channels, refine hwparams, prepare DMA slave config, and call the trigger helper for start/stop/pause/resume. Close paths release or keep channels depending on the helper variant and registration mode.

## State and Persistence
Per-substream runtime state includes the selected DMA channel, prepared slave config, cyclic DMA descriptor state, and ALSA runtime hw constraints. `dmaengine_pcm` persists for the component lifetime. No disk persistence exists.

## Dependencies and Integration Points
It depends on ALSA PCM, ASoC component APIs, and Linux DMAengine. It is a shared integration layer for many SoC audio drivers and DAI drivers.

## Risks and Edge Cases
Direction mapping assumes only playback and capture streams. Flag semantics matter: `SND_DMAENGINE_PCM_FLAG_COMPAT`, `NO_DT`, and `HALF_DUPLEX` change channel acquisition and concurrency. Incorrect `fifo_size`, `maxburst`, or `addr_width` can cause DMA corruption or audio glitches. Channel lifetime differs between `close` and `close_release_chan`.

## Test Signals
Build coverage for users, playback/capture open/close, trigger command matrix, cyclic DMA residue/position behavior, DT and non-DT channel acquisition, half-duplex enforcement, and suspend/resume sync-stop behavior are useful.
