# sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-pdm-dma.c

## Purpose
This platform driver implements the ACP6.3/ACP7.x PDM DMA capture component used for digital microphones. It exposes an ASoC component and DAI named `acp_ps_pdm_dma.0`, programs the PDM ring buffer and page table entries, manages PDM DMA start/stop, handles period interrupts through the PCI parent, and restores capture state after resume.

## Important APIs, Types, And Functions
Important entry points are `acp63_pdm_audio_probe()`, `acp63_pdm_dma_open()`, `acp63_pdm_dma_hw_params()`, `acp63_pdm_dai_trigger()`, `acp63_pdm_dma_pointer()`, `acp63_pdm_dma_close()`, `acp63_pdm_resume()`, `acp63_pdm_suspend()`, and `acp63_pdm_runtime_resume()`. Hardware helpers include `acp63_config_dma()`, `acp63_init_pdm_ring_buffer()`, `acp63_enable_pdm_clock()`, `acp63_start_pdm_dma()`, `acp63_stop_pdm_dma()`, and interrupt-mask helpers guarded by the parent ACP mutex.

## Control Flow
Probe maps the parent-provided MMIO resource, obtains the parent `acp63_dev_data` lock, registers the component and DAI, and enables runtime PM. Open allocates `struct pdm_stream_instance`, installs fixed capture hardware constraints, enables PDM interrupts, and records `capture_stream`. `hw_params` writes PTE entries for the runtime DMA buffer and sets ring-buffer address, size, and watermark. Trigger start programs channel count and decimation, snapshots the byte counter, and starts PDM DMA if not already active; stop checks status and stops/flushed DMA. Pointer reports ALSA position from the PDM linear position counter modulo buffer size.

## State And Persistence Behavior
Per-stream state is allocated in `runtime->private_data` with DMA address, page count, base MMIO pointer, and baseline byte count. Device state in `struct pdm_dev_data` keeps the capture substream and shared ACP lock. The module parameter `pdm_gain` is clamped to 0..3 and written into `ACP_WOV_MISC_CTRL` when enabling the PDM clock. Resume reprograms PTEs and ring buffer if a capture stream remains open, then reenables interrupts.

## Dependencies And Integration Points
It depends on the PCI parent for platform-device creation, MMIO resource, top-level IRQ dispatch, and parent `acp_lock`. The parent IRQ handler calls `snd_pcm_period_elapsed()` on `capture_stream` when `PDM_DMA_STAT` is observed. The machine driver `ps-mach.c` binds this DAI to `dmic-codec`.

## Risks And Edge Cases
Only 48 kHz stereo S32_LE capture is supported; unexpected channels return `-EINVAL`. Stop/start polling can return `-ETIMEDOUT`, which should propagate to ALSA trigger failures. The open path returns `-EINVAL` on allocation failure instead of `-ENOMEM`. Interrupt masking is shared with other ACP users, so lock coverage around `ACP_EXTERNAL_INTR_CNTL` is important. A stale `capture_stream` would cause period callbacks after close, but close clears it before freeing private data.

## Test Signals
Validate `arecord` at 48 kHz, 2 channels, S32_LE; invalid channel counts; period elapsed cadence; pointer monotonicity and wrap; suspend/resume while capture is open; runtime suspend/resume with no open stream; and `pdm_gain` values outside 0..3 clamping as expected in hardware register writes.
