# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-gs101-ufs.c

Purpose: Provides Google Tensor GS101 UFS PHY calibration, hibern8 transition tables, and custom calibration/CDR wait callbacks for the shared Samsung UFS PHY core.

Important APIs and functions: Exports `tensor_gs101_ufs_phy`. Tables include `tensor_gs101_pre_init_cfg`, `tensor_gs101_pre_pwr_hs_config`, `tensor_gs101_post_pwr_hs_config`, `tensor_gs101_post_h8_enter`, and `tensor_gs101_pre_h8_exit`. Custom callbacks are `gs101_phy_wait_for_calibration()` and `gs101_phy_wait_for_cdr_lock()`.

Control flow: The common core applies pre-init data then waits for RX calibration done at transceiver register `0x338` per lane. Later HS calibration applies pre/post power tables. Hibern8 enter/exit notifications program the dedicated hibern8 tables; on hibern8 exit the common core invokes the GS101 CDR wait callback, which polls register `0x339` and toggles CDR enable bits in register `0x222` until lock.

State and persistence: This file is static drvdata plus hardware-programming tables. Runtime hardware state includes PMA common/transceiver registers, hibern8-specific overrides, CDR enable toggles, and PMU isolation at `TENSOR_GS101_PHY_CTRL`.

Dependencies and integration points: Depends on `phy-samsung-ufs.h`, the common Samsung UFS PHY driver, one `ref_clk`, and the `google,gs101-ufs-phy` compatible. It integrates with UFS controller hibern8 notifications through `notify_phystate`.

Risks: The pre-HS config array lacks an explicit `END_UFS_PHY_CFG` sentinel in the visible table, so the following static object layout is important to inspect if changing it. Calibration and CDR waits use per-lane offsets and fixed retry timing. Hibern8 tables directly affect low-power entry/exit stability.

Test signals: GS101 UFS boot, RX calibration done polling, CDR recovery after HS mode and hibern8 exit, hibern8 enter/exit cycles, two-lane operation, PMU isolation, and timeout/error logs under marginal link conditions.
