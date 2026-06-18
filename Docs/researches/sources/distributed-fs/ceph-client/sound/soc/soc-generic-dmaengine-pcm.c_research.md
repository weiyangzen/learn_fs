# sources/distributed-fs/ceph-client/sound/soc/soc-generic-dmaengine-pcm.c

## Purpose
This file provides the generic ASoC platform component implementation for PCM devices backed by the Linux DMAEngine API. It bridges ALSA/ASoC PCM callbacks to DMAEngine helpers, registers a `snd_soc_component`, requests DMA channels from device tree or legacy filters, preallocates managed DMA buffers, and handles optional per-channel sample processing for copy-based access.

## Important APIs, Types, and Functions
The exported entry points are `snd_dmaengine_pcm_prepare_slave_config()`, `snd_dmaengine_pcm_register()`, and `snd_dmaengine_pcm_unregister()`. The runtime object is `struct dmaengine_pcm`, reached through `soc_component_to_pcm(component)`, with `config`, `flags`, and `chan[SNDRV_PCM_STREAM_*]`. `snd_dmaengine_pcm_prepare_slave_config()` converts ALSA hardware parameters to `struct dma_slave_config`, then overlays DAI DMA data from `snd_soc_dai_get_dma_data()`. It explicitly rejects multi-CPU links.

PCM component callbacks include `dmaengine_pcm_open()`, `dmaengine_pcm_close()`, `dmaengine_pcm_hw_params()`, `dmaengine_pcm_trigger()`, `dmaengine_pcm_pointer()`, `dmaengine_copy()`, `dmaengine_pcm_new()`, and `dmaengine_pcm_sync_stop()`. Two component driver tables exist: `dmaengine_pcm_component` for normal mmap/interleaved operation and `dmaengine_pcm_component_process` when `config->process` requires a `.copy` hook.

## Control Flow
Registration allocates `struct dmaengine_pcm`, installs a default config if none is supplied, requests OF DMA channels via `dmaengine_pcm_request_chan_of()`, chooses the component driver variant, initializes the component, and adds it to ASoC. PCM creation later calls `dmaengine_pcm_new()` for each stream: missing channels are requested by configured names, OF defaults (`tx`, `rx`, or `rx-tx` for half duplex), or the compatibility filter path. Open sets runtime hardware limits from either `config->pcm_hardware` or DAI DMA metadata, then opens the DMAEngine PCM helper. `hw_params` runs the configured `prepare_slave_config()` and calls `dmaengine_slave_config()`.

## State and Persistence
Persistent in-kernel state is the registered component plus requested DMA channels. The module parameter `prealloc_buffer_size_kbytes` defaults buffer preallocation to 512 KiB unless overridden by the config. `SND_DMAENGINE_PCM_FLAG_NO_RESIDUE` is set when DMA capabilities report descriptor-only residue or caps cannot be queried; pointer reporting then switches to period counting and exposes `SNDRV_PCM_INFO_BATCH`.

## Dependencies and Integration Points
The file depends on DMAEngine (`dma_request_chan`, `dma_get_slave_caps`, `dmaengine_slave_config`), ALSA DMAEngine PCM helpers, ASoC DAI DMA data, OF phandles/channel names, and ASoC component registration. Drivers integrate by calling `snd_dmaengine_pcm_register()` with `struct snd_dmaengine_pcm_config`, optional channel names, `compat_request_channel`, `prepare_slave_config`, `pcm_hardware`, and optional `process`.

## Risks and Test Signals
The largest behavioral risks are unsupported multi-CPU links, wrong DMA channel naming, half-duplex channel sharing, residue granularity assumptions, and callback ordering during error cleanup. `dmaengine_copy()` relies on channel-interleaved buffer offset math and must keep playback/capture copy ordering intact around `process()`. There is no local KUnit in this file; useful validation is boot/probe coverage for OF and legacy DMA paths, ALSA playback/capture smoke tests, residue/pointer tests on DMA engines with different granularity, and unregister/reprobe leak checks.
