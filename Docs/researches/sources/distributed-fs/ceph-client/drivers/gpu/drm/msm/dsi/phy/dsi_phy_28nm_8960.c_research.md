# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_28nm_8960.c

Purpose: 28nm 8960/A-family DSI PHY and PLL support. This is a separate legacy PLL topology with custom byte-divider behavior, 27 MHz reference clock, calibration/regulator sequencing, and 8960-specific lane/timing registers.

Important APIs and functions:
- `struct dsi_pll_28nm`, `struct pll_28nm_cached_state`, and `struct clk_bytediv` implement VCO state and a custom byte divider.
- `dsi_pll_28nm_clk_set_rate()`, `_recalc_rate()`, `_is_enabled()`, `_vco_prepare()`, `_vco_unprepare()`, and `_clk_determine_rate()` implement VCO operations.
- `get_vco_mul_factor()` and `clk_bytediv_*()` choose the VCO multiple from requested byte clock and program POSTDIV2.
- `pll_28nm_register()` registers VCO, special byte divider, and pixel divider.
- `dsi_28nm_pll_save_state()/restore_state()`, `dsi_28nm_phy_calibration()`, `dsi_28nm_phy_lane_config()`, and `dsi_28nm_phy_enable()/disable()` implement state and PHY control.

Control flow: byte clock users configure the custom byte divider, which requests a parent VCO multiple of 8, 16, 32, or 64 depending on bit clock. Before VCO enable, `dsi_pll_28nm_vco_prepare()` derives the hidden bit divider from the byte divider, writes POSTDIV1, enables the PLL, and polls the ready bit. PHY enable computes timing, initializes regulator registers, configures LDO/strength/control, runs hardware calibration with busy polling, writes lane/BIST defaults, and commits timing.

State and persistence: cached state includes VCO rate plus three postdiv control registers. `phy->pll_on` tracks VCO power. Calibration status is transient and not persisted. The common PHY stores the computed timing and handles external regulator lifetime.

Dependencies and integration points: uses `qcom,dsi-phy-28nm.h` clock indices, clk-provider divider helpers, `dsi_phy_28nm_8960.xml.h`, common timing math, regulator `vddio`, and two hard-coded resource starts for DSI0/DSI1.

Risks: the hidden bit-divider derivation divides byte divider by 8; unexpected divider values can underflow or misprogram. Calibration only waits until not busy and does not fail if timeout expires. Custom divider `set_rate()` ORs factor bits without clearing. The PLL reference and rate range differ from other 28nm code, so accidental config reuse is unsafe.

Test signals: byte-rate to VCO multiplier tests, PLL lock and recalc at 600 MHz to 1.2 GHz, calibration status observation, BIST/lane programming sanity, save/restore of postdivs, and both 8960 DSI resource starts.
