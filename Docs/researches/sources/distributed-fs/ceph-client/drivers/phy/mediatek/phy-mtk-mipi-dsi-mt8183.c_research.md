<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8183.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8183.c

Purpose: Provides MT8183-specific MIPI DSI TX PLL, calibration-data programming, and lane signal callbacks for the common MediaTek MIPI TX driver.

Important APIs and types: Exports `mt8183_mipitx_data`. Clock ops use `.enable`/`.disable` rather than prepare/unprepare, plus common set/recalc and rate clamping. Important helpers are `mtk_mipi_tx_pll_enable()`, `mtk_mipi_tx_pll_disable()`, `mtk_mipi_tx_config_calibration_data()`, and signal power callbacks.

Control flow: PLL enable chooses posdiv from data rates 125 MHz to 2+ GHz, powers SDM, clears PLL enable, de-isolates, computes PCW from 26 MHz, writes PLL control, sets posdiv, and enables PLL. Signal power-on powers bandgap in two stages, disables software control for all lanes, programs drive-strength-derived LDO reference, writes 10 calibration bits for each of five lanes using `rt_code[]`, and enables clock-lane clock mode. Power-off re-enables software control for lanes and powers down bandgap/pad state.

State and persistence: Uses `mipi_tx->data_rate`, `mipitx_drive`, and `rt_code[]` loaded by common code from DT/nvmem. Calibration bits persist in per-lane registers until reset or next power-on.

Dependencies and integration points: Consumed by common MIPI TX probe for `mediatek,mt8183-mipi-tx`. Relies on optional nvmem calibration and `drive-strength-microamp`.

Risks: Calibration bit addressing uses `MIPITX_D2P_RTCODE * (i + 1) + j * 4`, so register layout assumptions are critical. Missing calibration values are forced to default nibble values. Data rates below 125 MHz fail.

Test signals: MT8183 DSI panel modes across rate buckets, nvmem calibration present/missing cases, drive-strength clamping, lane register readback, and power cycle display tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8183.c -->
