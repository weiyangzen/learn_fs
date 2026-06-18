# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_10nm.c

Purpose: 10nm MSM DSI PHY and PLL implementation, including v3.0 PHY programming, PLL rate calculation, common-clock registration, DT tuning properties, bonded-DSI usecase handling, and two config variants for generic 10nm and 8998 old-timing hardware.

Important APIs and functions:
- `struct dsi_pll_10nm`, `struct pll_10nm_cached_state`, and `struct dsi_phy_10nm_tuning_cfg` carry PLL clock state, cached dividers/muxes, and per-lane drive tuning.
- PLL callbacks `dsi_pll_10nm_vco_set_rate()`, `dsi_pll_10nm_vco_prepare()`, `dsi_pll_10nm_vco_unprepare()`, `dsi_pll_10nm_vco_recalc_rate()`, and `dsi_pll_10nm_clk_determine_rate()` implement the VCO `clk_ops`.
- `pll_10nm_register()` builds the clock tree: VCO, out divider, bit divider, byte fixed factor, by-2 bit clock, post-out divider, pclk mux, and DSI pixel divider.
- `dsi_10nm_pll_save_state()` and `dsi_10nm_pll_restore_state()` cache and restore out-div, bit-div, pixel-div, mux, and VCO programming.
- `dsi_10nm_phy_enable()`, `dsi_10nm_phy_disable()`, and `dsi_10nm_phy_parse_dt()` implement PHY lane programming and optional DT drive-strength configuration.

Control flow: probe calls `dsi_pll_10nm_init()`, which registers clocks, stores the PLL in `pll_10nm_list`, performs an initial save-state handoff, and seeds `vco_current_rate`. A rate set computes decimal/fractional dividers, optional SSC values, commits PLL registers, writes frequency-independent PLL registers, and flushes. VCO prepare biases PLL rails, mirrors bias/global-clock to a bonded slave if present, reprograms rate, starts PLL, polls lock, enables global clocks, and enables RBUF. PHY enable calculates v3 D-PHY timings, waits for refgen ready, powers common blocks/lanes, writes timing registers, sets usecase, and commits lane strength/tuning registers.

State and persistence: persistent state lives in `vco_current_rate`, `cached_state`, `slave`, `postdiv_lock`, and `phy->tuning_cfg`. Save/restore is needed after PHY reset and for display handoff. DT tuning is persisted as unsigned masked register values after signed range validation.

Dependencies and integration points: uses common clock APIs, `readl_poll_timeout_atomic`, MMIO register XML headers, `msm_dsi_dphy_timing_calc_v3`, OF properties `qcom,phy-rescode-offset-top`, `qcom,phy-rescode-offset-bot`, and `qcom,phy-drive-ldo-level`. `dsi_10nm_set_usecase()` links master PLLs to `pll_10nm_list[(id + 1) % DSI_MAX]` and selects external PLL source for slaves.

Risks: `dsi_pll_10nm_vco_prepare()` reprograms from `vco_current_rate`; a stale zero/default can program an unintended VCO. The old-timing quirk changes lane `TX_DCTRL` behavior and must match silicon. Lane swap is TODO and fixed. DT offset validation reads into signed arrays through an unsigned OF helper pattern, so property encoding should be tested carefully. Slave lookup assumes both PHYs have probed.

Test signals: verify PLL lock at min/max rates, byte/pixel clock rate propagation through the clock tree, both standalone and bonded DSI, 8998 old timing, DT tuning boundaries `[-32,31]`, allowed LDO levels 375 through 500 mV, suspend/resume save/restore, and warnings when PHY is disabled with PLL still on.
