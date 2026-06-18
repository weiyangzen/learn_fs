# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-fsd-ufs.c

Purpose: Provides FSD SoC UFS PHY drvdata and a small set of calibration tables for the common Samsung UFS PHY driver.

Important APIs and functions: Exports `fsd_ufs_phy`. Tables are `fsd_pre_init_cfg`, empty `fsd_pre_pwr_hs_cfg`, empty `fsd_post_pwr_hs_cfg`, and `fsd_ufs_phy_cfgs`. It uses the common `samsung_ufs_phy_wait_for_lock_acq()` callback.

Control flow: Common UFS PHY code applies the pre-init table in the initial calibration stage and sees sentinel-only tables for HS pre/post stages. CDR lock polling uses status offset `0x6e`.

State and persistence: Only static tables and drvdata are defined here. Hardware state is PMA register programming and PMU isolation at offset `FSD_EMBEDDED_COMBO_PHY_CTRL`.

Dependencies and integration points: Depends on `phy-samsung-ufs.h` and the common driver. It binds to `tesla,fsd-ufs-phy`.

Risks: Minimal HS-stage tuning means stability depends on defaults and pre-init programming. The CDR status offset differs from Exynos7, so drvdata correctness is important. The compatible is vendor-specific and may have limited compile/runtime coverage.

Test signals: FSD UFS enumeration, PLL/CDR lock polling at `0x6e`, PMU isolation toggles, single `ref_clk` availability, and power-mode transitions despite empty HS tables.
