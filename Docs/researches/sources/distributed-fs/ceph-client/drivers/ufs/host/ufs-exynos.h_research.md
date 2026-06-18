# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-exynos.h

## Purpose
Defines Exynos UFS vendor register offsets, UniPro debug MIBs, PHY timing attribute layouts, SoC driver-data contracts, private host state, option flags, lane iteration helpers, and MMIO accessors used by `ufs-exynos.c`.

## Important APIs, types, and functions
Important types are `struct exynos_ufs_uic_attr`, `struct exynos_ufs_drv_data`, `struct ufs_phy_time_cfg`, and `struct exynos_ufs`. Driver-data callbacks cover SoC-specific init, pre/post link, pre/post power change, HCE enable, and suspend. Option flags such as `EXYNOS_UFS_OPT_BROKEN_AUTO_CLK_CTRL`, `EXYNOS_UFS_OPT_USE_SW_HIBERN8_TIMER`, `EXYNOS_UFS_OPT_UFSPR_SECURE`, and `EXYNOS_UFS_OPT_SKIP_CONFIG_PHY_ATTR` gate behavior in the C file. Macros generate `hci_*`, `unipro_*`, and `ufsp_*` accessors.

## Control flow and state
The header itself has no runtime flow, but it defines all persistent variant state: mapped MMIO windows, PHY handle, clocks, available lanes, timing config, hibern8 timestamp, sysreg IO coherency fields, SoC data, and options.

## Dependencies and integration points
Depends on UFSHCD types, Linux PHY, clocks, regmap, and UniPro constants from included C context. It is the ABI between static SoC tables and generic Exynos variant logic.

## Risks and test signals
Risks include incorrect register offsets, stale timing constants, option flags that interact subtly, and mutable `uic_attr` tables modified during DT parse. Test signals are compile coverage for all Exynos compatibles, correct MMIO accessors, and runtime validation of lane iteration, timing computation, and SoC option combinations.
