# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos7-ufs.c

Purpose: Supplies Exynos7 UFS PHY calibration tables and drvdata for the common Samsung UFS PHY driver.

Important APIs and functions: Exports `exynos7_ufs_phy`. Register programming data is split into `exynos7_pre_init_cfg`, `exynos7_pre_pwr_hs_cfg`, and `exynos7_post_pwr_hs_cfg`, referenced by `exynos7_ufs_phy_cfgs`. Clock list is `tx0_symbol_clk`, `rx0_symbol_clk`, `rx1_symbol_clk`, and `ref_clk`.

Control flow: The common UFS PHY driver applies the pre-init table at PHY power-on, then advances through post-init, pre-HS power mode, and post-HS power mode calibration states as callers invoke `.calibrate`. Exynos7 uses the common `samsung_ufs_phy_wait_for_lock_acq()` as `wait_for_cdr` after post-HS programming.

State and persistence: This file contains static const tables only. Hardware state is written by the common driver to PMA common and transmit/receive blocks, and PMU isolation is controlled through offset `EXYNOS7_EMBEDDED_COMBO_PHY_CTRL`.

Dependencies and integration points: Depends on `phy-samsung-ufs.h` macros and the common Samsung UFS PHY core. It integrates with the `samsung,exynos7-ufs-phy` compatible via common match data.

Risks: Table values are magic SoC tuning values and include order-sensitive comments. Lane offsets and CDR status offset must match Exynos7 hardware. Missing clocks or wrong PMU isolation masks prevent link startup.

Test signals: UFS link startup, HS-G1/G2 series A/B power-mode changes, PLL/CDR lock acquisition, clock enable coverage, and hibernate/resume behavior through the common driver even though this SoC has no hibern8-specific table.
