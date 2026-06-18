<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-dp.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-dp.c

Purpose: Implements a MediaTek DisplayPort PHY shim that programs lane driving defaults, link rate, spread-spectrum clocking, and a PHY digital reset through a regmap supplied by platform data.

Important APIs and types: `struct mtk_dp_phy` stores the regmap. PHY callbacks are `mtk_dp_phy_init()`, `mtk_dp_phy_configure()`, and `mtk_dp_phy_reset()`.

Control flow: Probe expects `dev->platform_data` to contain a `struct regmap **`, allocates state, creates a PHY, and optionally creates a non-DT lookup. Init bulk-writes the same six driving-parameter words to all four lanes. Configure maps DP link rates 1620, 2700, 5400, and 8100 Mbps to hardware bit-rate values when `opts->dp.set_rate` is set, and toggles SSC through `opts->dp.ssc`. Reset pulses `DP_GLB_SW_RST_PHYD` low then high with a short delay.

State and persistence: The driver stores only the regmap pointer. Hardware state persists in the shared DP PHY register block after init/configure/reset.

Dependencies and integration points: Uses generic PHY, platform driver binding by name rather than OF match, and a regmap supplied by a parent MediaTek DP device. DP controller code passes `phy_configure_opts_dp`.

Risks: Probe fails if platform data is absent, so it is tightly coupled to parent device instantiation. Unknown link rates return `-EINVAL`. Bulk write assumes contiguous driving registers and identical lane tuning.

Test signals: Parent-created platform device with regmap, four-lane driving register writes, rate changes for RBR/HBR/HBR2/HBR3, SSC on/off, reset pulse, and DP link training at each supported rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-dp.c -->
