# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_28nm.c

Purpose: mainstream 28nm DSI PHY and PLL implementation for HPM, family B, LP, 8226, and 8937 variants. It registers the 28nm clock tree, programs integer/fractional PLL settings, handles HPM/LP/8226 lock sequences, caches PLL dividers, and enables legacy D-PHY lanes/regulators.

Important APIs and functions:
- `struct dsi_pll_28nm` and `struct pll_28nm_cached_state` store VCO clock state and cached postdiv/mux registers.
- `dsi_pll_28nm_clk_set_rate()`, `_recalc_rate()`, `_is_enabled()`, `_clk_determine_rate()`, and the three prepare variants (`_hpm`, `_lp`, `_8226`) implement PLL clock behavior.
- `pll_28nm_register()` registers VCO, analog postdiv, indirect path /2, pixel divider, byte mux, and byte fixed-factor clock.
- `dsi_28nm_pll_save_state()` and `dsi_28nm_pll_restore_state()` cache `POSTDIV3`, `POSTDIV1`, byte mux, and optionally VCO rate.
- `dsi_28nm_phy_enable()` and `dsi_28nm_phy_disable()` program D-PHY timing, regulator mode, strength, lane registers, global test bit-clock selection, and power-down.

Control flow: rate setting forces postdiv2 to /4, chooses loop-filter resistance from `lpfr_lut`, selects integer versus SDM mode based on reference-clock divisibility, writes SDM/calibration registers, and respects LP-specific delay. VCO prepare is quirk-selected: HPM retries a full power sequence up to three times, LP uses nanosecond-level sequencing and a different lock-detect toggle, and 8226 uses its own calibration and retry loop. PHY enable calculates legacy timing, enables LDO or DCDC regulator mode, writes timing and lane defaults, and sets `BITCLK_HS_SEL` based on DSI id/usecase.

State and persistence: PLL cache stores dividers/mux and `vco_rate`, with restore re-running set-rate and writing cached dividers. `phy->pll_on` is set/cleared by prepare/unprepare. Quirk flags persist per config and drive LP/8226 behavior.

Dependencies and integration points: uses dt clock bindings, common clock framework, `dsi_phy_28nm.xml.h`, common `msm_dsi_dphy_timing_calc()`, regulator `vddio`, and configs referenced by compatible strings in `dsi_phy.c`.

Risks: multiple silicon paths share much code but differ in delay and lock requirements; regressions can be variant-specific. `clk_bytediv_set_rate()` ORs divider bits rather than clearing first, so callers rely on reset or prior state. LPFR lookup can reject out-of-table VCO rates. Fixed lane programming ignores lane masks. Save-state sets VCO rate to zero if PLL is off; restore must not be called with an invalid cached rate in unexpected paths.

Test signals: lock tests for HPM, LP, and 8226 variants; rate recalc comparison against requested byte/pixel clocks; regulator LDO and DCDC modes; save/restore after reset; DSI1 slave/standalone bit-clock selection; and boot tests for all exported configs.
