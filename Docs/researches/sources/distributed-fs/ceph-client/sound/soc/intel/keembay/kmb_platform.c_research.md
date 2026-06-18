# sources/distributed-fs/ceph-client/sound/soc/intel/keembay/kmb_platform.c

## Purpose
Implements the Intel Keem Bay I2S/HDMI-I2S/TDM ASoC CPU DAI and platform component, supporting DMA operation when DT `dmas` are present and interrupt-driven PIO operation otherwise.

## Important APIs, Types, And Functions
Key routines include PIO transfer helpers `kmb_pcm_tx_fn()`, `kmb_pcm_rx_fn()`, HDMI IEC958 conversion `hdmi_reformat_iec958()`, IRQ handler `kmb_i2s_irq_handler()`, DAI ops `kmb_set_dai_fmt()`, `kmb_dai_trigger()`, `kmb_dai_hw_params()`, `kmb_dai_prepare()`, `kmb_dai_startup()`, and `kmb_dai_hw_free()`, plus probe `kmb_plat_dai_probe()`. It registers DAI variants `intel_kmb_hdmi_dai`, `intel_kmb_i2s_dai`, and `intel_kmb_tdm_dai`.

## Control Flow, State, And Persistence
Probe maps I2S and PSS registers, prepares APB/osc clocks, reads FIFO depth, chooses PIO vs DMA, registers the component, and disables channels at boot. Runtime state lives in `struct kmb_i2s_info`: active stream count, configured channel count/rate/width, FIFO threshold, DMA addresses, PIO substream pointers, buffer positions, and IEC958 mode. `hw_params` programs data width, transfer resolution, channel mode, clock-provider limits, PSS config, and optional bit clock rate. Trigger starts/stops I2S, IRQs, or DMA handshakes.

## Dependencies And Integration Points
Depends on DT compatible strings `intel,keembay-i2s`, `intel,keembay-hdmi-i2s`, and `intel,keembay-tdm`, MMIO resources, `apb_clk`, `osc`, optional IRQ, optional DMA channels, ASoC, and dmaengine PCM.

## Risks And Test Signals
Risks include active-count imbalance, PIO pointer races, 2-channel master-only restrictions, multi-channel capture requiring clock-consumer mode, IEC958 in-place buffer mutation, optional IRQ with PIO mode, and DMA stop split between trigger and `hw_free`. Test signals include playback/capture for S16/S24/S32/IEC958, DMA and PIO paths, two/four/eight channel cases, clock-provider format combinations, underrun/overrun logs, and suspend/remove clock cleanup.
