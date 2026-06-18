# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s_tdm.c

Purpose: Rockchip I2S/TDM controller DAI driver. It extends the base I2S model with TDM slots, separate TX/RX master clocks, reset controls, synchronized TX/RX clock modes, optional IO multiplexing, path routing, and SoC-specific GRF setup.

Important APIs, types, and functions: `struct rk_i2s_tdm_dev` holds clocks, resets, regmap/GRF, DMA data, SoC data, master/TDM/multiplex flags, frame width, TRCM mode, lane routes, refcount, and DAI pointer. DAI ops include `set_fmt`, `hw_params`, `trigger`, `set_sysclk`, `set_bclk_ratio`, and `set_tdm_slot`. Helpers handle MCLK enable, runtime PM, reset/clear (`rockchip_snd_xfer_clear`), shared TRCM start/stop (`rockchip_snd_txrxctrl`), IO multiplex, path validation/config, and SoC GRF init.

Control flow: Probe reads TRCM sync properties, initializes DAI capabilities from `dma-names`, gets GRF/resets/clocks, maps registers, configures DMA addresses, validates optional TX/RX route arrays, enables clocks, sets DMA watermarks and TRCM bits, runs SoC init, then registers component and dmaengine PCM. `set_fmt` writes master/slave, inversion, base format, and TDM frame-sync/shift fields when TDM mode is active. `hw_params` sets clock rates/dividers, width/channel fields, optionally updates both TX/RX in synchronized TRCM mode while pausing active transfer, and applies IO multiplex constraints. Trigger starts/stops TX, RX, or shared TX/RX depending on TRCM.

State and persistence: Regmap uses flat cache and PM sync. `refcount` under spinlock coordinates shared synchronized transfer. `mclk_tx_freq` and `mclk_rx_freq` cache target sysclk values from machine drivers. Path arrays persist after DT parsing.

Dependencies and integration: Depends on clocks `hclk`, `mclk_tx`, `mclk_rx`, optional resets `tx-m`/`rx-m`, optional `rockchip,grf`, generic DMAEngine PCM, SoC match data for PX30/RK1808/RK3308/RK3568/RV1126, and DT properties for TRCM, IO multiplex, and lane routes.

Risks and edge cases: Synchronized reset admits a race because reset bulk atomicity is unavailable. Refcount underflow would break shared transfer if trigger calls are unbalanced. TRCM non-TXRX requires GRF; missing GRF fails SoC init. IO multiplex supports only a 10-channel aggregate constraint. Route properties must provide exactly four unique entries.

Test signals: Probe matrix should cover SoCs with and without SoC data. Playback/capture/TDM slot tests should validate dividers, frame width, and route fields. Duplex synchronized TRCM should start both sides together, pause safely on hw_params changes, and clear/reset on stop. Suspend/resume should sync regcache.
