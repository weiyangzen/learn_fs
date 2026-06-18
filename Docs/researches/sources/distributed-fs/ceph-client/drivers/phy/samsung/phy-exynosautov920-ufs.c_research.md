# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynosautov920-ufs.c

Purpose: Supplies ExynosAuto v920 UFS PHY tables and a custom CDR lock recovery callback for the common Samsung UFS PHY driver.

Important APIs and functions: Exports `exynosautov920_ufs_phy` and `exynosautov920_ufs_phy_wait_cdr_lock()`. Tables include a large `exynosautov920_pre_init_cfg`, small `exynosautov920_pre_pwr_hs_cfg`, empty post-HS table, and `exynosautov920_ufs_phy_cfgs`. The transceiver lane offset is 0x200.

Control flow: The common driver writes the pre-init table during initial power-on and pre-HS table before HS mode. On post-HS CDR wait, the custom callback polls a per-lane CDR lock register at `EXYNOSAUTOV920_CDR_LOCK_OFFSET` plus lane offset. If lock is absent, it repeatedly disables/enables CDR through register `0x222`; on lock it writes a final register `0x246` value and returns success.

State and persistence: Static drvdata controls PMU isolation offset `0x708`, single `ref_clk`, and CDR status offset. The custom wait mutates PMA transceiver registers during recovery loops.

Dependencies and integration points: Depends on common Samsung UFS code and `phy-samsung-ufs.h`. It binds through `samsung,exynosautov920-ufs-phy`.

Risks: The wait loop uses fixed 40 us delays and 100 retries, so marginal hardware may time out. CDR recovery writes are lane-specific and must match the 0x200 lane layout. The large pre-init table is highly hardware-specific, with little semantic validation possible in software.

Test signals: UFS link startup on ExynosAuto v920, two-lane CDR lock behavior, timeout logging, HS mode transitions, PMU isolation state, and regression testing after hibernate/power cycles.
