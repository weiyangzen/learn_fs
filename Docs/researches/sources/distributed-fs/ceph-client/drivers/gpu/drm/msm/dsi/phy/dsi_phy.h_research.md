# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy.h

Purpose: internal contract for MSM DSI PHY implementations. It defines the revision operation table, configuration records, timing data container, runtime PHY object, exported config symbols, and timing helper prototypes shared by the common core and per-node PHY files.

Important APIs and types:
- `struct msm_dsi_phy_ops` is the revision hook table: `pll_init`, `enable`, `disable`, `save_pll_state`, `restore_pll_state`, `set_continuous_clock`, and `parse_dt_properties`.
- `struct msm_dsi_phy_cfg` describes a compatible's regulators, operations, PLL min/max rates, resource base addresses used for PHY id detection, quirk flags, and whether separate regulator/lane windows exist.
- `struct msm_dsi_dphy_timing` stores all D-PHY timing registers plus shared host-visible fields and legacy v2 half-byte/prep-delay fields.
- `struct msm_dsi_phy` is the live device state: platform device, MMIO bases/sizes, id, supplies, timing, config, optional tuning data, usecase, mode flags, VCO clock, PLL power state, provided clocks, and save-state marker.

Control flow: revision files fill `msm_dsi_phy_cfg.ops`, the common probe binds one config to one `struct msm_dsi_phy`, and callers invoke only the common exported functions. Timing calculation prototypes centralize the shared math in `dsi_phy.c` while hardware files only commit register values.

State and persistence: the header makes `state_saved`, `pll_on`, `usecase`, `regulator_ldo_mode`, and `cphy_mode` explicit cross-file state. `provided_clocks` has `NUM_PROVIDED_CLKS`, sized around `DSI_PIXEL_PLL_CLK + 1`, so each PLL implementation must populate the expected byte and pixel indices.

Dependencies and integration points: includes dt clock bindings, clk-provider, delay, regulator consumer, and local `dsi.h` for DSI constants and clock request/usecase definitions. Exported `dsi_phy_*_cfgs` are consumed by the common OF table and compiled conditionally via Kconfig in `dsi_phy.c`.

Risks: this header is a tight ABI within the driver. Adding fields or ops requires all revision files to keep coherent semantics. `io_start` based indexing is fragile for new SoCs. Misstating `has_phy_lane` or `has_phy_regulator` causes probe-time mapping failures or missing register programming.

Test signals: build all PHY variants, validate every exported config referenced by `dsi_phy_dt_match`, test D-PHY and C-PHY timing callers, and verify clock-provider consumers see both `DSI_BYTE_PLL_CLK` and `DSI_PIXEL_PLL_CLK`.
