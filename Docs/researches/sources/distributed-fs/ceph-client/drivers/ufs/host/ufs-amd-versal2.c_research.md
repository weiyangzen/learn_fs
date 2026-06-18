# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-amd-versal2.c

## Purpose
Implements AMD Versal Gen 2 UFS platform support on top of DesignWare UFSHCD. It handles resets, firmware-mediated calibration readiness, PHY register access through DME sideband registers, PHY enable, and power-mode-specific rate/adaptation programming.

## Important APIs, types, and functions
`struct ufs_versal2_host` stores reset controls, host clock rate, PHY mode, and ATT/CTLE calibration bytes read from firmware. `ufs_versal2_phy_reg_read()` and `_write()` access PHY registers through `CBCREG*` MIBs and `VS_MPHYCFGUPDT`. `ufs_versal2_phy_init()` waits for `zynqmp_pm_is_mphy_tx_rx_config_ready()`, programs RMMI attributes, deasserts PHY reset, waits for SRAM init, applies calibration, and enables MPHY FSMs. `ufs_versal2_pwr_change_notify()` handles fallback to slow mode when no calibration exists, selects HS rate, toggles RX override/ack, and configures initial adapt for 2-lane HS.

## Control flow and state
`ufs_versal2_init()` allocates the variant state, records the `core` clock rate, obtains and asserts host/PHY resets, asks firmware to bypass SRAM, deasserts host reset, reads calibration values, and sets `UFSHCD_QUIRK_SKIP_DEF_UNIPRO_TIMEOUT_SETTING`. HCE post-change initializes PHY; link pre-change writes `DWC_UFS_REG_HCLKDIV`; link post-change delegates to DWC startup notification.

## Dependencies and integration points
Depends on ZynqMP firmware APIs, reset controller, clock list naming, DesignWare UFS MIB definitions, UFSHCD platform probing, and UniPro power attributes.

## Risks and test signals
Risks include firmware readiness timeout, missing calibration forcing slow mode, incorrect clock name `core`, reset ordering, and polling loops with one-second microsecond counters. Test signals are firmware calls succeeding, TX/RX FSMs reaching Hibern8/Sleep/LSBurst, link startup with correct HCLKDIV, HS mode only on calibrated parts, and successful suspend/runtime PM through UFSHCD callbacks.
