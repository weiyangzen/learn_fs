# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_7nm.c

Purpose: modern 7nm-family DSI PHY and PLL implementation reused by 7nm, 5nm, 4nm, and 3nm Qualcomm SoCs. It supports D-PHY and C-PHY timing, multiple hardware minor-version quirks, high-rate PLL programming, common-clock registration, continuous clock control, bonded DSI, REFGEN voting, and many SoC-specific config records.

Important APIs and functions:
- `struct dsi_pll_7nm` adds VCO state, postdiv and mux locks, PLL bias reference counting, cached dividers/mux, and bonded slave pointer.
- `dsi_pll_7nm_vco_set_rate()`, `_prepare()`, `_unprepare()`, `_recalc_rate()`, `_lock_status()`, and `_clk_determine_rate()` implement VCO operations.
- `dsi_pll_enable_pll_bias()` and `dsi_pll_disable_pll_bias()` protect common control and PLL mux state with `pll_enable_lock` plus `pll_enable_cnt`.
- `pll_7nm_register()` builds D-PHY or C-PHY-aware byte and pixel clock trees; C-PHY uses /7-style factors and fixes the DSI clock parent to post-out-div.
- `dsi_7nm_phy_enable()`, `dsi_7nm_phy_disable()`, `dsi_7nm_set_usecase()`, `dsi_7nm_set_continuous_clock()`, and PLL save/restore are the core runtime paths.

Control flow: PLL set-rate enables bias, computes decimal/fractional values and quirk-specific clock inverter settings, writes PLL programming and frequency-independent registers, optionally writes SSC registers, disables bias, and flushes. Prepare enables local and slave bias, starts PLL, polls lock, resets PHY digital logic after analog collapse, enables global clocks and RBUF, and marks `pll_on`. PHY enable calculates C-PHY or D-PHY v4 timings, optionally votes REFGEN for newer quirks, waits for refgen ready, selects voltage/strength/rescode settings by quirk, rate, and C-PHY mode, powers common blocks and lanes, sets usecase, writes timing registers, and writes lane settings.

State and persistence: `pll_enable_cnt` prevents unbalanced PLL bias power changes and rate-limits imbalance errors. Save-state caches out-div, bit/pixel dividers, and DSICLK mux while temporarily enabling bias. `vco_current_rate`, `slave`, `cphy_mode`, `usecase`, `pll_on`, and quirk flags strongly influence restore and clock-tree behavior.

Dependencies and integration points: uses `linux/bitfield.h`, clk-provider, `readl_poll_timeout_atomic`, XML register headers, common timing calculators `msm_dsi_dphy_timing_calc_v4()` and `msm_dsi_cphy_timing_calc_v4()`, DSI usecase enums, and compatible-selected configs in `dsi_phy.c`.

Risks: many SoC variants share one code path with quirk-dependent magic values, making regressions subtle. C-PHY support is present but marked with TODOs in parts of the enable path. REFGEN vote sequencing is required only on newer quirks. Slave linkage assumes both PHYs are initialized. Bias reference counting catches underflow but cannot repair missed enables/disables. 32-bit builds cap max PLL rate at `ULONG_MAX`, which differs from 64-bit 5 GHz configs.

Test signals: D-PHY and C-PHY mode tests, rate sweeps through inverter threshold bands, REFGEN vote on V4.3/V5.2/V7.2, continuous clock bit toggling, bonded master/slave external PLL selection, suspend/resume save/restore, 32-bit build coverage, and smoke tests for each exported 7nm/5nm/4nm/3nm config.
