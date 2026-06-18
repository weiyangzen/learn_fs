# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_sai.c

## Purpose
Implements the Rockchip SAI ASoC CPU DAI driver for `rockchip,rk3576-sai`. It exposes playback and/or capture DAIs depending on DT `dma-names`, configures I2S/left/right-justified/DSP/TDM framing, drives DMA through `snd_dmaengine`, handles runtime PM and regmap caching, and reports FIFO/frame-sync failures through IRQs.

## Important APIs, Types, And Functions
- `struct rk_sai_dev` is the full device state: clocks, reset controls, regmap, DMA descriptors, active PCM substreams, lane routing arrays, version, TDM/frame-pulse mode, master/slave state, and `xfer_lock`.
- DAI operations are collected in `rockchip_sai_dai_ops`: `.startup`, `.shutdown`, `.hw_params`, `.set_fmt`, `.set_sysclk`, `.prepare`, `.trigger`, and `.set_tdm_slot`.
- `rockchip_sai_set_fmt()` translates `SND_SOC_DAIFMT_*` master/slave, inversion, and data format flags into `SAI_CKR`, `SAI_TXCR`, `SAI_RXCR`, shift, and frame-sync programming.
- `rockchip_sai_hw_params()` chooses lanes, word width, slot width, frame width, DMA burst, and master-mode BCLK divider from PCM parameters.
- `rockchip_sai_start()`, `rockchip_sai_stop()`, `rockchip_sai_xfer_start()`, `rockchip_sai_xfer_stop()`, and `rockchip_sai_clear()` drive transfer lifecycle and FIFO clear/reset recovery.
- `rockchip_sai_parse_paths()` reads optional `rockchip,sai-tx-route` and `rockchip,sai-rx-route` DT properties and maps logical paths to SDO/SDI lanes.
- `rockchip_sai_isr()` handles TX underrun, RX overrun, frame-sync error, and frame-sync lost interrupts, stopping affected PCM substreams on xruns.
- `rockchip_sai_probe()` owns allocation, reset lookup, MMIO/regmap setup, IRQ, clocks, version read, DAI construction, route parsing, runtime PM setup, DMA PCM registration, and component registration.

## Control Flow
Probe builds a per-device DAI based on available `tx`/`rx` DMA names, initializes default FIFO thresholds, parses optional lane routes, enables runtime PM, registers a dmaengine PCM, and registers the ASoC component. At stream startup, only one substream per direction is accepted and optional mixer-configured PCM wait time is copied into the substream. `set_fmt` stops or clears the hardware before changing clock provider/polarity/format fields. `hw_params` programs stream-specific lane count, sample width, slot count, frame width, DMA burst, and, in master mode, validates that `mclk_rate` can exactly derive the requested BCLK. `prepare` enables master clocks and frame-sync detection. Trigger start enables DMA and stream bits; trigger stop disables DMA, waits for stream idle, and clears FIFO logic. Runtime suspend disables frame-sync detection, stops/gates transfer clocks, switches regmap to cache-only, delays for BCLK leakage avoidance, then disables `mclk` and `hclk`; resume re-enables clocks and syncs cached registers.

## State And Persistence
Runtime state is in `rk_sai_dev` and hardware registers cached by regmap. `mclk_rate` is set by `.set_sysclk`; `wait_time[]` is user-visible ALSA control state and is applied to future substreams. `substreams[]` tracks active ALSA streams so the IRQ path can call `snd_pcm_stop_xrun()`. `initialized`, `is_master_mode`, `is_tdm`, `fpw`, and route/lane arrays persist for the device lifetime. There is no disk persistence.

## Dependencies And Integration Points
Depends on Linux ASoC, dmaengine PCM, regmap, runtime PM, reset controls, clocks, device tree, IRQ handling, and `rockchip_sai.h`. Integrates with machine drivers through standard CPU DAI callbacks, `SND_SOC_DAIFMT_*`, TDM slot APIs, `set_sysclk`, DMA channel names `tx`/`rx`, and optional DT lane route properties. Register accessibility, volatility, and precious RX data semantics are declared through `rockchip_sai_regmap_config`.

## Risks And Edge Cases
- Master-mode BCLK generation is strict: `mclk_rate` must match an integer divider within `CLK_SHIFT_RATE_HZ_MAX`, so machine drivers must call `.set_sysclk` correctly.
- `set_fmt` and TDM changes intentionally stop clocks and streams; misuse while active can cause audible glitches despite locking.
- `rockchip_sai_clear()` falls back to full reset and regcache sync on timeout, which can recover hardware but may hide timing bugs.
- Frame-sync lost detection in slave mode assumes CRU SCLK equals external SCLK; the comment flags this as a hardware/clocking caveat.
- Lane routing validates only array length and lane index, so invalid board-level topology may still pass software checks.
- IRQ is optional; without it xrun/frame-sync diagnostics and automatic substream stop are absent.

## Test Signals
Useful validation includes probe with DT variants containing tx-only, rx-only, and full duplex DMA names; ALSA playback/capture across supported formats and rates; TDM slot enable/disable; lane route DT property tests; suspend/resume and runtime autosuspend; induced TX underrun/RX overrun IRQ handling; and checking regmap cache sync after reset and PM transitions.
