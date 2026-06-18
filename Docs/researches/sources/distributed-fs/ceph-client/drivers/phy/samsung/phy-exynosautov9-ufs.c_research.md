# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynosautov9-ufs.c

Purpose: Provides ExynosAuto v9 UFS PHY calibration tables and drvdata for the shared Samsung UFS PHY driver.

Important APIs and functions: Exports `exynosautov9_ufs_phy`. Tables are `exynosautov9_pre_init_cfg` and `exynosautov9_pre_pwr_hs_cfg`, referenced by `exynosautov9_ufs_phy_cfgs`. The file defines an Auto v9 lane offset helper `PHY_TRSV_REG_CFG_AUTOV9()` using a 0x50 transmit/receive channel offset.

Control flow: The common driver applies the pre-init table when powering on in the initial state, later applies the pre-HS power-mode table during calibration, and uses the common lock acquisition helper for CDR status after post-HS state if invoked.

State and persistence: Static tables and drvdata are the only software state. Runtime hardware state is PMA register contents and PMU isolation at offset `0x728`.

Dependencies and integration points: Depends on `phy-samsung-ufs.h`, common UFS PHY probe/match handling, a single `ref_clk`, and the `samsung,exynosautov9-ufs-phy` compatible.

Risks: The custom transceiver channel offset differs from the default, so using default macros would program the wrong lane. The tables cover no explicit post-HS entries, so link stability relies on pre-init/pre-HS values plus common CDR wait.

Test signals: Probe with one `ref_clk`, UFS link startup, HS-G3 series B power mode, PMU isolation toggle, CDR lock status at `0x5e`, and lane programming on single- and multi-lane configurations.
