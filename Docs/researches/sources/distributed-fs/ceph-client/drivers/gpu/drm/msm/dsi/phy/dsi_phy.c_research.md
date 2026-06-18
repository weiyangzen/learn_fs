# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy.c

Purpose: common Qualcomm MSM DSI PHY core. It supplies generic D-PHY/C-PHY timing calculators, selects per-process-node PHY configuration from device tree, maps PHY register windows, registers PLL clock providers, and exposes the enable/disable/save/restore/snapshot entry points used by the DSI host.

Important APIs and functions:
- `msm_dsi_dphy_timing_calc()`, `_v2()`, `_v3()`, `_v4()` and `msm_dsi_cphy_timing_calc_v4()` convert requested bit and escape clock rates into register timing fields in `struct msm_dsi_dphy_timing`.
- `dsi_phy_driver_probe()` allocates `struct msm_dsi_phy`, resolves its hardware index from the `dsi_phy` resource start address, maps `dsi_phy`, `dsi_pll`, optional `dsi_phy_lane`, and optional `dsi_phy_regulator`, gets regulators, attaches runtime PM/pm-clk, initializes the process-specific PLL, and registers the onecell clock provider.
- `msm_dsi_phy_enable()` resumes runtime PM, enables supplies, delegates hardware programming to `cfg->ops.enable`, copies shared timings back to the caller, and restores PLL state after PHY reset when this PHY is not a slave.
- `msm_dsi_phy_disable()`, `msm_dsi_phy_set_usecase()`, `msm_dsi_phy_set_continuous_clock()`, `msm_dsi_phy_pll_save_state()`, `msm_dsi_phy_pll_restore_state()`, and `msm_dsi_phy_snapshot()` are the external control surface for host, clock, and debug code.

Control flow: probe is configuration-driven through `dsi_phy_dt_match`, which maps compatible strings to `struct msm_dsi_phy_cfg` instances compiled from the revision files. Enable flow is layered: common PM and regulator setup happens first, revision-specific register writes happen through `ops.enable`, shared timing values are returned, and cached PLL register state is restored if needed. Disable reverses only the common rails/PM plus the revision-specific power-down hook.

State and persistence: `struct msm_dsi_phy` persists mapped bases, size metadata for snapshots, regulator handles, the last computed timing block, usecase, LDO/CPHY mode flags, VCO clock handle, `pll_on`, onecell clock data, and `state_saved`. PLL save/restore is deliberately stateful because a PHY reset can silently reset PLL registers while the common clock framework still believes rates/dividers are programmed.

Dependencies and integration points: depends on Linux platform driver, OF match data, runtime PM, pm-clk, regulators, clk-provider, dt-bindings `phy-type`, MSM helpers such as `msm_ioremap_size()` and `msm_disp_snapshot_add_block()`, and revision files that export `dsi_phy_*_cfgs`. The DSI host consumes the clock provider through `DSI_BYTE_PLL_CLK` and `DSI_PIXEL_PLL_CLK`.

Risks: timing math is integer-heavy and rate-sensitive; zero rates are rejected but extreme rates can still expose rounding or register-width assumptions. `dsi_phy_get_id()` assumes fixed resource base addresses in each config. Save/restore depends on every revision hook caching the right registers before reset. Runtime PM, regulator, and PLL restore error unwinding must remain ordered to avoid powered partially configured PHY blocks.

Test signals: compile with each `CONFIG_DRM_MSM_DSI_*_PHY` variant, boot DTs for each compatible, verify `of_clk_hw_onecell_get` provides byte/pixel clocks, exercise DSI modes across low/high bit rates, suspend/resume or display handoff paths that trigger PLL save/restore, and inspect `msm_dsi_phy_snapshot()` output when PLL is on and off.
