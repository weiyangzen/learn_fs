<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8173.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8173.c

Purpose: Supplies MT2701/MT8173 MIPI DSI TX PLL and lane signal operations for the common MediaTek MIPI TX driver.

Important APIs and types: Exports `mt2701_mipitx_data` and `mt8173_mipitx_data`. Clock ops implement prepare/unprepare, determine-rate, set-rate via common helper, and recalc via common helper. Signal callbacks enable or disable lane LDO outputs and pad tie-low.

Control flow: PLL prepare chooses TX dividers based on cached `data_rate` from 50 MHz to 1.25 GHz, powers bandgap, programs impedance/bias, enables LDO core/output, powers SDM, clears PLL enable, writes dividers and fractional PCW derived from 26 MHz, enables fractional mode and PLL, disables SSC, and writes the SoC preserve value. Unprepare disables PLL, clears preserve, isolates/powers down SDM, disables HS bias/LDOs/bandgap, and clears dividers. Signal enable sets LDO output on clock and four data lanes and clears pad tie-low; disable reverses it.

State and persistence: `mipi_tx->data_rate` is cached by common set-rate. `mppll_preserve` differs between MT2701 and MT8173. Register state persists until unprepare/power-off.

Dependencies and integration points: Used by `phy-mtk-mipi-dsi.c` aggregate driver through match data. Depends on common nvmem/drive-strength fields only indirectly.

Risks: Unsupported data rates outside 50 MHz to 1.25 GHz fail prepare. PLL math assumes 26 MHz reference. MT2701 and MT8173 share logic but differ preserve value; adding variants needs careful register compatibility review.

Test signals: DSI panel bring-up on MT2701 and MT8173, data-rate buckets at boundaries, PLL PCW readback, lane LDO/pad tie behavior, and display blank/unblank cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8173.c -->
