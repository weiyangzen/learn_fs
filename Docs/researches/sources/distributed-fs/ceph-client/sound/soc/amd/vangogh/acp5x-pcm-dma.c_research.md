# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-pcm-dma.c

## Purpose
This platform driver implements Vangogh ACP5x PCM DMA for SP and HS I2S playback/capture. It provides ALSA PCM hardware constraints, DMA PTE/ring-buffer programming, shared IRQ handling, pointer reporting, and runtime/system PM restore.

## Important APIs, Types, And Functions
Main functions are `i2s_irq_handler()`, `config_acp5x_dma()`, `acp5x_dma_open()`, `acp5x_dma_hw_params()`, `acp5x_dma_pointer()`, `acp5x_dma_new()`, `acp5x_dma_close()`, `acp5x_audio_probe()`, `acp5x_pcm_resume()`, `acp5x_pcm_suspend()`, and `acp5x_pcm_runtime_resume()`. The component is named `acp5x_i2s_dma`.

## Control Flow
Probe consumes IRQ flags from platform data, maps the ACP MMIO resource, gets the IRQ, registers the ASoC component, requests the IRQ, and enables runtime PM. Open allocates `struct i2s_stream_instance` and applies playback/capture constraints. `hw_params` reads card platform info to route playback/capture to HS or SP, stores the substream in the appropriate active pointer, computes page count, and calls `config_acp5x_dma()`. IRQ handling acknowledges HS/SP TX/RX threshold bits and calls `snd_pcm_period_elapsed()`. Resume reprograms DMA and sample/TDM registers for all active stream pointers and reenables external interrupts.

## State And Persistence Behavior
Device state persists active substream pointers for HS playback/capture and SP playback/capture plus TDM settings shared with DAI state. Per-stream private data persists DMA address, page count, selected instance, transfer resolution, byte count, and clock dividers. Close clears the active pointer and frees stream private data.

## Dependencies And Integration Points
It depends on the Vangogh PCI parent for resources and IRQ flags, `acp5x.h` for register constants and helpers, `acp5x-i2s.c` for DAI format/trigger control, and `acp5x-mach.c` for routing through `acp5x_platform_info`.

## Risks And Edge Cases
`hw_params` fails if machine driver data is missing, making this component dependent on a correctly registered card. Resume writes fixed HS or SP sample registers based on stored active pointers; stale pointers would misprogram hardware. The DMA interrupt control register is programmed with all four threshold bits whenever any stream configures DMA. Tests should verify interrupt behavior with simultaneous SP and HS streams.

## Test Signals
Run SP headset playback/capture and HS speaker playback on supported boards, period interrupt validation for all four threshold bits, pointer wrap tests, repeated open/close memory checks, runtime suspend/resume interrupt gating, and system resume with active TDM and non-TDM streams.
