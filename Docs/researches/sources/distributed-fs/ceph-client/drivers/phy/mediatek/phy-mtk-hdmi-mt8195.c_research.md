<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.c

Purpose: Implements MT8195 HDMI PHY PLL, TMDS/FRL-related analog setup, HDMI 2.0 clock ratio handling, and a fixed 5 V regulator for HDMI power output.

Important APIs and types: Exports `mtk_hdmi_phy_8195_conf`. Important functions include `mtk_hdmi_pll_calc()`, `mtk_hdmi_pll_set_hw()`, `mtk_hdmi_pll_drv_setting()`, clock ops prepare/unprepare/set_rate/determine_rate/recalc_rate, `mtk_hdmi_phy_configure()`, and regulator ops for `hdmi-pwr5v`.

Control flow: Set-rate calculates PLL parameters for 25 to 594 MHz TMDS clocks. It selects TX position divider, finds a TX predivider that keeps ICO clock between 5 and 12 GHz, computes a 33-bit fractional feedback word, chooses digital divider, then writes hardware fields for prediv, feedback, posdiv stages, TX pre/pos dividers, and digital pixel divider. Prepare enables serializer/driver operation bits, disables FRL lane bits, applies bias/impedance settings based on pixel/TMDS range, powers bandgap/LDOs, powers PLL, clears isolation, and unpowers PLL. Configure sets PLL rate from `opts->dp.link_rate` and toggles HDMI 2.0 clock ratio for TMDS above 340 MHz. Regulator ops set, clear, and read the HDMI 5 V output bit.

State and persistence: `hdmi_phy->pll_rate` and `tmds_over_340M` are cached. Hardware analog/PLL and regulator state persists until unprepare, disable, or regulator operation.

Dependencies and integration points: Integrated by common HDMI driver, uses MT8195 register definitions in `phy-mtk-hdmi-mt8195.h`, field helpers, clk framework, generic PHY configure, and regulator core.

Risks: The configure path uses `phy_configure_opts_dp` for HDMI-specific link rate, which is an unusual API contract. PLL arithmetic has multiple boundary checks and integer divisions; boundary modes need coverage. Regulator state is direct MMIO without external enable tracking.

Test signals: Pixel clocks from 25 to 594 MHz, 340 MHz TMDS ratio transition, regulator enable/disable/is_enabled, HDMI 2.0 modes, invalid rate rejection, clock recalc, and suspend/resume preserving expected off state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.c -->
