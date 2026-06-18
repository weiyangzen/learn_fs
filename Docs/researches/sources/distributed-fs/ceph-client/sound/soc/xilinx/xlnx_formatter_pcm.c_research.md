# sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_formatter_pcm.c

## Purpose
ASoC PCM platform driver for Xilinx audio formatter IP. It controls MM2S playback and S2MM capture formatter engines, manages PCM buffers, period interrupts, AES channel-status parsing, and formatter-specific hw_params.

## Important APIs, Types, and Functions
Key structs are `xlnx_pcm_drv_data` and `xlnx_pcm_stream_param`. Important functions include `xlnx_parse_aes_params()`, `xlnx_formatter_pcm_reset()`, `xlnx_formatter_disable_irqs()`, IRQ handlers `xlnx_mm2s_irq_handler()` and `xlnx_s2mm_irq_handler()`, component callbacks `xlnx_formatter_set_sysclk()`, `xlnx_formatter_pcm_open()`, `xlnx_formatter_pcm_close()`, `xlnx_formatter_pcm_pointer()`, `xlnx_formatter_pcm_hw_params()`, `xlnx_formatter_pcm_trigger()`, `xlnx_formatter_pcm_new()`, and platform probe/remove.

## Control Flow, State, and Persistence
Probe enables `s_axi_lite_aclk`, maps the formatter registers, reads core configuration to detect MM2S/S2MM engines, resets present engines, disables interrupts, requests named IRQs, stores driver data, and registers the ASoC component. Open validates engine presence, allocates per-stream private data, reads format/channel/xfer-mode limits, installs PCM constraints, enables IOC IRQs, and stores active substream pointers for IRQ callbacks. Hw_params validates channels, programs playback MCLK multiplier if sysclk is known, optionally logs AES RX parameters, writes DMA buffer address, sample width, active channels, period configuration, and bytes-per-channel. Trigger toggles DMA enable; pointer reads transfer count. Close resets the stream engine, disables IRQs, and frees stream state.

## Dependencies and Integration Points
Depends on ALSA SoC component PCM APIs, managed PCM buffers, Linux MMIO/platform IRQ/clock APIs, and IEC958 channel-status definitions. It pairs with Xilinx I2S/SPDIF DAIs in machine graphs as the PCM platform component.

## Risks and Test Signals
Risks include memory leak on `open()` constraint failure after allocating `stream_data`, not clearing old data-width/active-channel bits before ORing new values, close returning success even if reset failed, active substream pointers not cleared on close, fixed two-channel PCM hardware despite reading channel limits, and reliance on named IRQs. Test signals are MM2S/S2MM detection, reset timeout handling, period IRQs, pointer wrap behavior, sysclk/rate divisibility, 64-byte period/buffer alignment, AES_TO_PCM logging, and playback/capture start/stop cycles.
