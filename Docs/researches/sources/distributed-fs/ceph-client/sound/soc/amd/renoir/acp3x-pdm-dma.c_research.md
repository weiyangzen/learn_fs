# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/acp3x-pdm-dma.c

## Purpose
This is the Renoir ACP3x PDM DMA capture driver for DMIC. It provides the ASoC component/DAI, programs PDM DMA buffers, handles PDM IRQ period notifications, and restores active capture state after runtime or system resume.

## Important APIs, Types, And Functions
Key callbacks are `acp_pdm_audio_probe()`, `acp_pdm_dma_open()`, `acp_pdm_dma_hw_params()`, `acp_pdm_dai_trigger()`, `acp_pdm_dma_pointer()`, `acp_pdm_dma_close()`, `acp_pdm_resume()`, `acp_pdm_runtime_suspend()`, and `acp_pdm_runtime_resume()`. Hardware helpers include `pdm_irq_handler()`, `config_acp_dma()`, `init_pdm_ring_buffer()`, `enable_pdm_clock()`, `start_pdm_dma()`, and `stop_pdm_dma()`.

## Control Flow
Probe reads IRQ flags from platform data, maps the ACP MMIO resource, gets the platform IRQ, registers component and DAI, requests the IRQ, and enables runtime PM. Open allocates stream private data, applies fixed 48 kHz stereo capture constraints, enables PDM interrupts, and records the capture substream. `hw_params` writes PTEs and ring-buffer/watermark registers. Trigger start sets channel count and decimation, snapshots byte count, and starts DMA if needed; trigger stop stops and flushes active DMA.

## State And Persistence Behavior
Device state in `struct pdm_dev_data` stores the IRQ, base pointer, and active capture stream. Per-stream state stores page count, DMA address, baseline byte count, and base pointer. The `pdm_gain` module parameter is clamped and written into `ACP_WOV_MISC_CTRL`. Resume restores PTEs/ring buffer when capture is open and reenables PDM interrupts.

## Dependencies And Integration Points
It depends on the Renoir PCI parent for platform resources, IRQ flags, and child creation, on `rn_acp3x.h` for constants and read/write helpers, and on `acp3x-rn.c` machine registration for the DMIC card path.

## Risks And Edge Cases
`disable_pdm_interrupts()` uses `ext_int_ctrl |= ~PDM_DMA_INTR_MASK` rather than clearing the bit with `&= ~`, which can set many unrelated interrupt bits; this is a significant risk. Open returns `-EINVAL` for allocation failure. Capture hardware advertises S32_LE in PCM hardware while the DAI capture formats include S24_LE and S32_LE, which may expose constraint mismatches. Only two-channel capture is accepted.

## Test Signals
Test 48 kHz stereo capture, unsupported channels/formats, interrupt mask state after close/runtime suspend, trigger timeout behavior, long-run pointer wrap, and suspend/resume with an open capture stream. Register tracing should specifically verify `ACP_EXTERNAL_INTR_CNTL` after `disable_pdm_interrupts()`.
