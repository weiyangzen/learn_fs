<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8173.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8173.c

Purpose: Provides MT8173 HDMI PHY PLL and TMDS operations for the common MediaTek HDMI PHY driver.

Important APIs and types: Exports `mtk_hdmi_phy_8173_conf`. Clock ops are `mtk_hdmi_pll_prepare()`, `mtk_hdmi_pll_unprepare()`, `mtk_hdmi_pll_determine_rate()`, `mtk_hdmi_pll_set_rate()`, and `mtk_hdmi_pll_recalc_rate()`.

Control flow: Determine-rate stores requested PLL rate and chooses parent rate equal to rate below 74.25 MHz or half-rate above it. Set-rate selects pre-divider and TX divider buckets, programs PLL feedback and analog constants, and changes predriver impedance/bias based on whether the rate is below 165 MHz. Prepare enables PLL autocalibration, bias, PLL, bias LPF, and TX divider. TMDS enable only turns on serializer, predriver, and driver bits; power-off clears those bits.

State and persistence: `hdmi_phy->pll_rate` is cached because recalc returns the requested rate rather than reading register fields. IBIAS and impedance settings persist in hardware until the next rate change or disable.

Dependencies and integration points: Consumed by `phy-mtk-hdmi.c` through `mediatek,mt8173-hdmi-phy`. Uses common field helpers and DT-provided `mediatek,ibias`/`mediatek,ibias_up`.

Risks: Cached recalc can diverge from hardware if registers are changed outside this driver. Rate buckets and analog values are hardcoded and sensitive to HDMI mode boundaries. Parent-rate manipulation must match the display clock tree.

Test signals: HDMI modes around 27 MHz, 74.25 MHz, 165 MHz, and high TMDS rates; clk framework set/recalc behavior; TMDS off/on during display blanking; and IBIAS DT property validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8173.c -->
