<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt2701.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt2701.c

Purpose: Supplies MT2701-specific HDMI PHY clock and TMDS enable operations for the common MediaTek HDMI PHY driver.

Important APIs and types: Exports `mtk_hdmi_phy_2701_conf`. Internal clock ops implement `mtk_hdmi_pll_prepare()`, `mtk_hdmi_pll_unprepare()`, `mtk_hdmi_pll_set_rate()`, `mtk_hdmi_pll_determine_rate()`, and `mtk_hdmi_pll_recalc_rate()`.

Control flow: PLL prepare enables autocalibration, clears RLH, enables position divider, bias, PLL, clock LDO, SLDO, bias LPF, serializer, predriver, and driver with staged delays. Set-rate chooses TX position divider from target rate, programs prediv/posdiv/FBK/BIAS/impedance constants, and configures driver bias. Recalc derives rate from hardware prediv, feedback divider, TX posdiv, and optional /5 divider. TMDS enable/disable mirrors the full analog enable/disable sequence.

State and persistence: Rate is mostly hardware-derived; common `mtk_hdmi_phy` stores driver impedance and ibias values from DT. Register state persists while PLL/TMDS are enabled.

Dependencies and integration points: Uses `phy-mtk-hdmi.h` common structures and `phy-mtk-io.h` field helpers. The common HDMI probe selects this config via `mediatek,mt2701-hdmi-phy`.

Risks: `determine_rate()` accepts any rate without bounding, while set-rate uses coarse fixed feedback values. Prepare and TMDS enable duplicate sequencing, so call layering must avoid unexpected double programming. Analog timing is delay-sensitive.

Test signals: Clock registration through common driver, pixel clock set/recalc at low/mid/high rates, HDMI modes on MT2701, TMDS enable/disable during hotplug, and register readback of divider fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt2701.c -->
