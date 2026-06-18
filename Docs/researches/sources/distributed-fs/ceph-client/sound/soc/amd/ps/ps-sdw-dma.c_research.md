# sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-sdw-dma.c

## Purpose
This file implements the common SoundWire PCM DMA platform component for ACP6.3, ACP7.0, ACP7.1, and ACP7.2. It maps ALSA PCM streams to SoundWire manager instances and ACP DMA channel registers, programs page tables/ring buffers/watermarks, enables or disables DMA channels, and restores active streams after system resume.

## Important APIs, Types, And Functions
The component callbacks are `acp63_sdw_dma_open()`, `acp63_sdw_dma_hw_params()`, `acp63_sdw_dma_trigger()`, `acp63_sdw_dma_pointer()`, `acp63_sdw_dma_close()`, and `acp63_sdw_dma_new()`. Probe/remove are `acp63_sdw_platform_probe()` and `acp63_sdw_platform_remove()`. Key helpers are `acp63_config_dma()`, `acp63_configure_sdw_ringbuffer()`, `acp63_sdw_get_byte_count()`, `acp63_sdw_dma_enable()`, `acp63_restore_sdw_dma_config()`, and `acp70_restore_sdw_dma_config()`. Static register tables describe ACP63 and ACP70 SDW0/SDW1 stream register layouts.

## Control Flow
Open finds the CPU DAI's `amd_sdw_manager`, copies DAI id to `stream_id`, copies manager instance to the private stream, and applies fixed 48 kHz two-channel playback/capture constraints. `hw_params` selects the correct register table and interrupt bit based on ACP revision and manager instance, stores the substream in the matching stream array, programs PTEs and ring buffer registers, enables the relevant external interrupt bit, and writes the period watermark. Trigger writes the stream's DMA enable register and polls the adjacent status register until it matches. Resume iterates every possible live stream in both manager instances, replays PTE/ring-buffer/watermark programming, and reenables all SDW DMA interrupt masks for the relevant revision.

## State And Persistence Behavior
Per-stream state in `struct acp_sdw_dma_stream` holds stream id, SoundWire instance, DMA address, page count, and baseline byte count. Device state in `struct sdw_dma_dev_data` holds the MMIO base, revision, parent lock pointer, and per-revision arrays mapping active stream ids to ALSA substreams. Pointer state is derived from ACP linear position counters. Interrupt status is not consumed here; the PCI parent and `ps-common.c` mark and process period interrupts using these substream arrays.

## Dependencies And Integration Points
It depends on SoundWire CPU DAI driver data (`struct amd_sdw_manager`), ACP PCI-created platform resources, `acp63.h` register definitions and stream constants, and ALSA/ASoC PCM callbacks. It is registered as platform driver `amd_ps_sdw_dma` and is used by SoundWire machine drivers selected by `pci-ps.c`.

## Risks And Edge Cases
Register selection is dense and revision-specific; incorrect stream id or manager instance can index the wrong table or return `-EINVAL`. ACP63 SDW1 supports only one TX and one RX stream while ACP70 SDW1 supports six, so tests must distinguish both. Interrupt mask writes in `hw_params` do not use the parent lock even though shared interrupt control registers are modified elsewhere. Trigger polling requires the status register to equal exactly the boolean enable value. Resume reenables broad DMA masks even if only some streams were active.

## Test Signals
Run playback and capture over SDW0 and SDW1 on ACP63 and ACP70-class hardware, validate period interrupts for all stream ids, check trigger timeout paths, verify pointer wrap behavior, and suspend/resume with multiple active SoundWire streams. Build coverage with SoundWire enabled is required, and runtime testing should confirm the parent IRQ thread sees stream arrays populated by this component.
