# sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x-pcm-dma.c

## Purpose
This platform driver implements Raven ACP3x PCM DMA for I2S/SP and BT playback/capture. It supplies the ASoC component callbacks for buffer allocation, DMA page-table programming, IRQ-driven period notifications, pointer reporting, runtime PM, and resume restore.

## Important APIs, Types, And Functions
Main functions are `i2s_irq_handler()`, `config_acp3x_dma()`, `acp3x_dma_open()`, `acp3x_dma_hw_params()`, `acp3x_dma_pointer()`, `acp3x_dma_new()`, `acp3x_dma_close()`, `acp3x_audio_probe()`, `acp3x_resume()`, `acp3x_pcm_runtime_suspend()`, and `acp3x_pcm_runtime_resume()`. The component driver is named `acp3x_rv_i2s_dma`.

## Control Flow
Probe consumes platform IRQ flags from the PCI parent, maps MMIO, registers the PCM component, requests the shared ACP IRQ, and enables runtime PM. Open allocates `struct i2s_stream_instance`, applies playback or capture hardware constraints, and stores MMIO in private data. `hw_params` obtains card platform info, records the substream in one of four device fields based on direction and SP/BT instance, computes pages, and calls `config_acp3x_dma()`. The IRQ handler checks BT/SP TX/RX threshold bits, acknowledges each matching bit, and calls `snd_pcm_period_elapsed()`. Resume replays DMA setup and sample-format/TDM registers for active streams.

## State And Persistence Behavior
`struct i2s_dev_data` persists active substream pointers for BT playback/capture and SP playback/capture plus TDM settings. Each stream private object persists DMA address, page count, instance, transfer resolution, and baseline byte count. Runtime suspend disables external interrupts; runtime resume reenables them. Close clears the active substream pointer but does not free the private `i2s_stream_instance`, which is a notable ownership issue compared with newer drivers.

## Dependencies And Integration Points
It depends on the Raven PCI parent for platform resources and IRQ flags, `acp3x.h` for register helpers and constants, the CPU DAI driver for format/trigger setup, and the card's `acp3x_platform_info` for instance routing.

## Risks And Edge Cases
The missing `kfree()` in `acp3x_dma_close()` can leak stream private data over repeated opens. The pointer helper in `acp3x.h` appears to OR high and low words rather than shifting high into the upper 32 bits, so long-running position values may be wrong. IRQ handling assumes active stream pointers are cleared before future interrupts for a stopped stream. A missing card platform info only prints `pinfo failed` but still continues to program DMA with whatever instance is in private data.

## Test Signals
Run repeated open/close leak detection, SP and BT playback/capture, IRQ threshold period notifications, pointer accuracy under long captures/playback, runtime suspend interrupt gating, and system resume with active TDM streams. KASAN/Kmemleak would be useful for close-path validation.
