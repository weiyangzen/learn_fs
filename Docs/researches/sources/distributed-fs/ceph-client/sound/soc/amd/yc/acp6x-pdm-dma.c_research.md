# sources/distributed-fs/ceph-client/sound/soc/amd/yc/acp6x-pdm-dma.c

## Purpose
This file implements the Yellow Carp ACP6x PDM DMA ASoC component and CPU DAI for two-channel, 48 kHz, 32-bit digital microphone capture. It programs ACP WOV/PDM registers, maps ALSA buffers through the ACP ATU/PTE scratch area, handles position reporting, and participates in runtime/system PM.

## Important APIs, Types, And Functions
The hardware contract is `acp6x_pdm_hardware_capture`. Core helpers include `acp6x_init_pdm_ring_buffer()`, `acp6x_enable_pdm_clock()`, `acp6x_start_pdm_dma()`, `acp6x_stop_pdm_dma()`, `acp6x_config_dma()`, and `acp6x_pdm_get_byte_count()`. ASoC component callbacks are `open`, `close`, `hw_params`, `pointer`, and `pcm_new`; the DAI operation is `acp6x_pdm_dai_trigger()`. Probe maps MMIO and registers `acp6x_pdm_component` plus `acp6x_pdm_dai_driver`. Module parameter `pdm_gain` controls `ACP_WOV_GAIN_CONTROL`.

## Control Flow
Probe maps the parent-provided ACP memory resource, stores `pdm_dev_data`, registers the component, then enables autosuspend. On PCM open it allocates a `pdm_stream_instance`, constrains periods, enables PDM interrupts, and stores the capture substream. `hw_params` configures page-table entries and ring-buffer/watermark registers. Trigger start sets channel count and decimation, snapshots the byte counter, and starts PDM DMA if not already active. Trigger stop stops DMA and flushes the FIFO. Pointer reads the hardware linear position counter and wraps it by buffer size.

## State And Persistence
Persistent driver state is `pdm_dev_data` with MMIO base and active capture stream. Per-stream state is allocated in `runtime->private_data` and stores page count, DMA address, starting byte counter, and MMIO base. Hardware state spans ACP WOV enable bits, ring-buffer registers, PDM clock/gain, ATU page tables in scratch registers, and interrupt masks.

## Dependencies And Integration Points
It depends on `acp6x.h` constants and MMIO helpers, platform resources from `pci-acp6x.c`, the PCI parent IRQ path that calls `snd_pcm_period_elapsed()`, ASoC component registration, and managed DMA buffers from the parent device.

## Risks And Test Signals
Risk areas include timeout polling, pointer wrap arithmetic, missing `kfree()` in close for `pdm_stream_instance`, global `pdm_gain`, and resume reprogramming while a stream is active. Test signals are successful capture at 48 kHz S32_LE stereo, stable period interrupts, correct `aplay/arecord` pointer movement, clean runtime suspend/resume, and no DMA timeouts or ACP error interrupts.
