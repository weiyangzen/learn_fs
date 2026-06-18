<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.c

Purpose: Provides common MediaTek MIPI DSI TX PHY glue: PLL clock registration, generic PHY power operations, drive-strength handling, optional nvmem calibration extraction, and OF dispatch to SoC-specific callbacks.

Important APIs and types: Exports common clock helpers `mtk_mipi_tx_pll_set_rate()` and `mtk_mipi_tx_pll_recalc_rate()`, plus `mtk_mipi_tx_from_clk_hw()`. Common PHY callbacks are `mtk_mipi_tx_power_on()` and `mtk_mipi_tx_power_off()`. Probe uses `struct mtk_mipitx_data` match data.

Control flow: Probe loads SoC data, maps registers, gets the reference clock, reads/clamps `drive-strength-microamp` with default 4600 uA, reads `clock-output-names`, registers the PLL `clk_hw`, creates the PHY, registers the PHY provider, stores `dev`, reads optional `calibration-data` nvmem into five RT codes, and registers the clock provider. Power-on enables the PLL clock then calls SoC signal enable. Power-off disables signals then the PLL clock.

State and persistence: `data_rate`, drive strength, `rt_code[]`, MMIO base, and SoC data are stored in `struct mtk_mipi_tx`. Hardware PLL and lane settings persist while powered.

Dependencies and integration points: Integrates generic PHY, clk provider, nvmem, OF match data, and SoC files for MT2701/MT8173/MT8183. Display DSI host drivers consume both the PHY and PLL clock.

Risks: Function name `mtk_mipi_tx_get_calibration_datal` has a typo but is internal. Optional nvmem failures are informational. Clock registration must happen before consumers request the PLL. Drive-strength range is clamped silently after warning.

Test signals: Probe each compatible, PLL clock set-rate/recalc, nvmem present/absent paths, invalid drive-strength warning and clamp, panel enable/disable, and runtime PM or suspend cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.c -->
