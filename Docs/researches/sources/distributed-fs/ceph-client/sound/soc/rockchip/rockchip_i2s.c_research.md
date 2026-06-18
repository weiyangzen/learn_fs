# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s.c

Purpose: Rockchip I2S controller CPU DAI driver using regmap and generic DMAEngine PCM. It supports playback/capture up to 8 channels, 8-192 kHz, S8/S16/S20_3LE/S24/S32 formats, optional GRF pin direction routing, and runtime PM.

Important APIs, types, and functions: `struct rk_i2s_dev` owns clocks, regmap, GRF regmap, DMA data, capability flags, TX/RX active flags, master-mode flag, bclk ratio, pinctrl states, and spinlock. Key DAI ops are `rockchip_i2s_set_fmt`, `rockchip_i2s_hw_params`, `rockchip_i2s_trigger`, `rockchip_i2s_set_bclk_ratio`, `rockchip_i2s_set_sysclk`, and DAI probe. Register access policy is defined by `rockchip_i2s_*_reg`; probe initializes clocks, regmap, DAI capabilities from `dma-names`, pinctrl, PM, component, and dmaengine PCM.

Control flow: `set_fmt` resumes PM and programs master/slave, inversion, and I2S/left/right/DSP formats in TXCR/RXCR/CKR. `hw_params` computes BCLK/LRCK dividers in master mode, programs sample width and channel select, optionally writes GRF IO direction from TX channel count, sets DMA watermarks, and configures clock mode for symmetric links. Trigger enables/disables DMA and XFER bits per stream, coordinating shared stop/clear when both TX and RX are idle and toggling optional BCLK pinctrl.

State and persistence: Register state is cached with REGCACHE_FLAT; runtime suspend cache-only disables MCLK, resume syncs cache after enabling MCLK. `tx_start`/`rx_start` are protected by spinlock. DAI caps are determined once from DT.

Dependencies and integration: Depends on clocks `i2s_hclk` and `i2s_clk`, optional `rockchip,grf`, optional pinctrl states `bclk_on/off`, DMA request names `tx`/`rx`, ALSA SoC, regmap, PM runtime, and generic DMAEngine PCM.

Risks and edge cases: `pm_runtime_get_sync` return is not checked in `set_fmt`. GRF routing derives direction from TXCR even for capture cases. Static `symmetric_rate` behavior changes TRCM to TX-only under some link conditions. Missing `bclk_off` when `bclk_on` exists fails probe.

Test signals: Probe should expose playback/capture only when corresponding DMA names exist. `aplay`/`arecord` should start XFER and DMA bits, then clear on stop. Runtime suspend/resume should preserve register configuration. Multi-channel tests should validate GRF IO direction.
