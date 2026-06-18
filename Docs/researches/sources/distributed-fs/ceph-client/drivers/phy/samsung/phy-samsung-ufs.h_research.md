# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-ufs.h

Purpose: Defines the shared data model, register-table macros, power-mode descriptors, state ids, structures, inline helpers, and extern drvdata declarations used by the Samsung UFS PHY common driver and SoC-specific table files.

Important APIs and functions: Key macros are `PHY_COMN_REG_CFG()`, `PHY_TRSV_REG_CFG_OFFSET()`, `PHY_TRSV_REG_CFG()`, `END_UFS_PHY_CFG`, `PHY_APB_ADDR()`, `PWR_MODE*` helpers, `PHY_PLL_LOCK_BIT`, and `PHY_CDR_LOCK_BIT`. Structures include `samsung_ufs_phy_cfg`, `samsung_ufs_phy_pmu_isol`, `samsung_ufs_phy_drvdata`, and `samsung_ufs_phy`. Inline helpers are `get_samsung_ufs_phy()` and `samsung_ufs_phy_ctrl_isol()`. Function declarations expose lock wait and register programming helpers to variant files.

Control flow: Variant files build sentinel-terminated arrays of `samsung_ufs_phy_cfg` with common or transceiver block ids and power-mode descriptors. The common driver walks these arrays by `id`, writes lane-specific offsets, and uses drvdata callbacks for calibration and CDR waits. PMU isolation is controlled through the inline helper from common power paths.

State and persistence: Header-defined state fields persist the mapped PMA base, PMU regmap, clock bulk array, drvdata pointers, lane count, calibration state, and selected PHY mode. The macros encode APB byte offsets and second-lane transceiver offsets into static tables.

Dependencies and integration points: Depends on Linux generic PHY and regmap types. It couples the common UFS driver with Exynos7, ExynosAuto v9/v920, FSD, and GS101 drvdata definitions.

Risks: The sentinel convention requires every table to end with an entry whose `id` is zero. Power-mode descriptors are stored but the current common writer does not filter by `mode`, so table ordering and host call stage are the real selectors. `samsung_ufs_phy_ctrl_isol()` assumes PMU isolation polarity shared by all variants.

Test signals: Compile coverage for all extern drvdata providers, static inspection of table sentinels, two-lane offset checks, PMU isolation bit behavior, and staged calibration tests that confirm the common driver consumes table structures as intended.
