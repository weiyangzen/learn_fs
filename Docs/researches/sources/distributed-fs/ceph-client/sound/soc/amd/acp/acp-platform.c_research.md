# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-platform.c

## Purpose
`acp-platform.c` is the common ACP PCM component/DMA platform layer. It exposes ALSA PCM hardware capabilities, allocates per-stream state, programs ACP page tables and DMA descriptors, reports stream pointers from ACP byte counters, and registers the SoC component/DAIs selected by revision drivers.

## Important APIs, Types, and Functions
Exports are `config_pte_for_stream()`, `config_acp_dma()`, `acp_platform_register()`, and `acp_platform_unregister()`. Component callbacks are `acp_dma_open()`, `acp_dma_close()`, `acp_dma_hw_params()`, `acp_dma_pointer()`, and `acp_dma_new()`. It defines legacy and ACP6x/7x `snd_pcm_hardware` capabilities.

## Control Flow
On PCM open, the driver allocates `struct acp_stream`, selects hardware limits by ACP revision, installs DMA-size alignment and integer-period constraints, stores the stream in runtime private data, enables external interrupts, and adds the stream to `chip->stream_list` under `acp_lock`. `hw_params` calls `config_pte_for_stream()` and `config_acp_dma()` to map DMA pages into ACP SRAM scratch/PTE registers. Pointer reads ACP byte counters and converts the modulo buffer position to frames. Close removes the stream from the list and frees it.

## State and Persistence
Per-stream state records substream, DAI ID, IRQ bit, direction, register/PTE/FIFO offsets, and last byte counter. `chip->stream_list` tracks live streams for IRQ handling and resume restoration. Hardware register state lasts until stream reconfiguration or ACP reset; all memory is volatile.

## Dependencies and Integration Points
The file depends on ASoC component registration, ALSA managed buffers, DMA buffer addresses, ACP register definitions, common byte-count helpers, and revision DAI arrays passed through `chip->dai_driver`. Resume paths in revision drivers iterate `stream_list` and reuse `config_pte_for_stream()`/`config_acp_dma()`.

## Risks
DMA page programming assumes the ALSA buffer is represented by contiguous DMA addresses page by page. ACP70/71/72 use hard-coded PTE windows by DAI/direction; wrong `stream->dai_id` or direction maps audio to the wrong memory window. `acp_dma_pointer()` uses `stream->bytescount` as a baseline and depends on correct byte-counter restoration. Open error paths must free `stream`.

## Test Signals
Exercise playback/capture open/close, period/buffer alignment constraints, mmap and managed buffers, pointer monotonicity/wraparound, ACP70 SP/BT/HS/DMIC streams, concurrent streams in `stream_list`, and resume restoring all active streams without distorted audio.
