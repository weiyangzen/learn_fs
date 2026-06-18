# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/phy/dsi_phy_20nm.c

Purpose: 20nm DSI PHY register programming without an in-file PLL clock implementation. It programs legacy D-PHY timing, regulator/LDO selection, lane strength/configuration, and enable/disable sequencing for two PHY instances.

Important APIs and functions:
- `dsi_20nm_dphy_set_timing()` writes common timing fields into 20nm timing control registers, including bit 8 handling for `clk_zero`.
- `dsi_20nm_phy_regulator_ctrl()` selects LDO or non-LDO regulator mode using `phy->regulator_ldo_mode` and the separate regulator register window.
- `dsi_20nm_phy_enable()` calculates legacy timing via `msm_dsi_dphy_timing_calc()`, enables regulator controls, programs strength, global test/bitclk selection, data lanes, clock lane, timing registers, and finally enables PHY control.
- `dsi_20nm_phy_disable()` clears PHY enable and regulator calibration power.
- `dsi_phy_20nm_cfgs` exports supplies, register windows, and ops to the common core.

Control flow: the common core enables PM and regulators, then this file computes timing and performs a fixed register write sequence. The `BITCLK_HS_SEL` setting depends on `phy->id` and `phy->usecase`, so DSI1 standalone differs from other cases. A write memory barrier precedes the final enable register write.

State and persistence: no local heap state or PLL cache exists. Persistent behavior is limited to `phy->timing`, `phy->regulator_ldo_mode`, and `phy->usecase` from the common object. Disable leaves the common core to turn off external supplies and runtime PM.

Dependencies and integration points: depends on `dsi_phy.h`, `dsi.xml.h`, `dsi_phy_20nm.xml.h`, common timing math, common regulator bulk handling, and a separate `dsi_phy_regulator` MMIO mapping because `has_phy_regulator` is true.

Risks: fixed magic register values dominate behavior and have little runtime validation. The code powers all data lanes rather than checking active lane count. Regulator LDO versus DCDC mode must match board DT. There is no PLL save/restore hook in this file, so the surrounding clock source must not require revision-local restoration.

Test signals: smoke test DSI0/DSI1, standalone and paired usecases, LDO and non-LDO regulator modes, timing across supported bit rates, and shutdown ordering with register reads confirming `PHY_CTRL_0` and calibration power clear.
