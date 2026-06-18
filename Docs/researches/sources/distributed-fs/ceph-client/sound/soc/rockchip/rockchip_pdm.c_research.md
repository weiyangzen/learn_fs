# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_pdm.c

Purpose: Rockchip PDM capture controller DAI driver. It configures PDM clocks, decimation/sample-rate controls, channel paths, DMA read thresholds, high-pass filters, runtime PM, and generic DMAEngine PCM for capture-only audio.

Important APIs, types, and functions: `struct rk_pdm_dev` owns clocks, regmap, DMA data, reset, and hardware version. Clock helpers are `get_pdm_clk`, `get_pdm_ds_ratio`, `get_pdm_cic_ratio`, and `samplerate_to_bit`. DAI ops are `rockchip_pdm_set_fmt`, `rockchip_pdm_trigger`, and `rockchip_pdm_hw_params`. Probe sets version from compatible, gets optional reset, configures regmap/DMA, clocks, runtime PM, component, initial stopped RX state, optional `rockchip,path-map`, and dmaengine PCM.

Control flow: `hw_params` ignores playback, selects a parent PDM clock for the sample rate, sets the clock rate, programs fractional divider and reset for RK3308/RV1126 variants when changed, chooses CIC/DS ratio, enables HPF and PDM clock, programs left-justified mode for newer variants, sets sample width and path enables from channel count, and sets DMA read level to `8 * channels`. Trigger toggles DMA read and RX start/clear. Runtime PM enables/disables `pdm_clk` and `pdm_hclk`; system sleep marks regcache dirty and syncs on resume.

State and persistence: Register defaults are cached through regmap. `version` controls hardware-specific paths. Optional path-map writes lane routing once at probe. No persistent storage beyond clocks/registers.

Dependencies and integration: Depends on clocks `pdm_clk`/`pdm_hclk`, reset `pdm-m` for RK3308-like versions, compatible match data, rational approximation support, DMAEngine PCM, and ALSA SoC.

Risks and edge cases: `rockchip_pdm_path_parse` returns the count when path-map is absent or wrong; absent is accepted only when it is `-ENOENT`. Probe enables `hclk`, then runtime resume may enable it again when runtime PM is disabled path is used; remove disables both clocks explicitly. Fractional divider reset interrupts active capture if params change. Only even 2/4/6/8 channels are accepted.

Test signals: Probe should register capture-only DAI and DMA address at RXFIFO. Captures at 8-192 kHz and 2/4/6/8 channels should program expected DS/CIC ratios and produce samples. Suspend/resume should preserve configuration. Invalid path-map or channel counts should fail.
