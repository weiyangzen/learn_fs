# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-ufs.c

Purpose: Provides a small MediaTek UFS MPHY generic PHY driver. It manages the UFS PHY MMIO block and two clocks, switching the PHY between active operation and deep hibernation by forcing or releasing PLL, CDR, isolation, squelch, and DIFZ controls.

Important APIs, types, and flow: `struct ufs_mtk_phy` contains the device, mapped MMIO base, and two `clk_bulk_data` entries named `unipro` and `mp`. `ufs_mtk_phy_probe()` allocates state, maps resource 0, obtains the clocks, creates one generic PHY with `ufs_mtk_phy_ops`, stores drvdata, and registers `of_phy_simple_xlate`. `ufs_mtk_phy_power_on()` enables clocks and calls `ufs_mtk_phy_set_active()`. `ufs_mtk_phy_power_off()` calls `ufs_mtk_phy_set_deep_hibern()` and disables clocks.

Control flow and state behavior: Active mode releases PLL power/isolation force bits, powers CDR, releases CDR isolation, enables RX squelch, waits 1 microsecond, then clears forced DIFZ. Deep hibernation applies the inverse sequence: force DIFZ, force RX squelch off, force CDR isolation and power off, force PLL isolation, and force PLL power off. Runtime state is entirely hardware-register state plus clock enable state; no persistent software state is maintained after probe.

Dependencies and integration points: Uses the generic PHY framework, platform resource mapping, bulk clock API, OF matching for `mediatek,mt8183-ufsphy`, and MediaTek bit helpers from `phy-mtk-io.h`. It is intended to be consumed by a UFS host controller node through a simple PHY phandle.

Risks and test signals: Register sequencing is the main correctness contract; reversed order can leave PLL/CDR isolated or powered unexpectedly. The driver has no `.init`/`.exit`, so consumers must rely on power-on/off transitions. Tests should verify clock names in DT, probe deferral on missing clocks, repeated power cycles, suspend/resume hibernation behavior, and UFS link bring-up after active transition.
