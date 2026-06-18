# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-ufs.c

Purpose: Implements the common Samsung UFS PHY framework. It binds compatible-specific drvdata, maps PMA registers, controls PMU isolation, manages clocks, applies staged calibration tables, handles UFS hibern8 notifications, and exposes one generic PHY to UFS host drivers.

Important APIs and functions: Public helper exports within the driver family are `samsung_ufs_phy_config()` and `samsung_ufs_phy_wait_for_lock_acq()`. Generic PHY operations are `samsung_ufs_phy_init()`, `samsung_ufs_phy_exit()`, `samsung_ufs_phy_power_on()`, `samsung_ufs_phy_power_off()`, `samsung_ufs_phy_calibrate()`, `samsung_ufs_phy_set_mode()`, and `samsung_ufs_phy_notify_state()`. Probe is `samsung_ufs_phy_probe()`.

Control flow: Probe matches compatible data, maps `phy-pma`, resolves `samsung,pmu-syscon`, creates the generic PHY, copies isolation config, optionally overrides the PMU offset from the phandle argument, initializes clocks, and registers the PHY provider. Init records bus width as lane count and starts the calibration state machine at `CFG_PRE_INIT`. Power-on disables isolation, enables clocks, and performs pre-init calibration. Later calibrate calls apply the current stage table and advance through pre-init, post-init, pre-HS, post-HS, then wrap to pre-init. Notify-state applies hibern8 enter/exit tables and waits for CDR on exit if supported.

State and persistence: `struct samsung_ufs_phy` tracks PMA base, PMU regmap, clocks, drvdata, current config tables, isolation bits, lane count, calibration state, and current generic PHY mode. Hardware state persists in PMA common/transceiver registers, PMU isolation, and enabled clocks. Calibration state is volatile software state and resets on `.init`.

Dependencies and integration points: Depends on generic PHY, clk bulk, syscon/regmap, platform MMIO, OF match data, UFS PHY notify states, and SoC-specific drvdata from sibling files. It integrates with UFS host controller link startup, power-mode changes, and hibern8 transitions.

Risks: Calibration state advances even if a table is missing, so host call ordering must match expectations. `samsung_ufs_phy_config()` writes lane 1 only for transceiver-block entries and silently ignores common entries on lane 1. `samsung_ufs_phy_ctrl_isol()` writes inverted enable semantics (`isol ? 0 : en`), so PMU bit polarity must match all variants. Missing hibern8 tables are treated as no-op.

Test signals: Probe for all compatibles, lane count from `phy->attrs.bus_width`, staged calibration call sequence during UFS link startup and power-mode changes, clock and PMU isolation traces, PLL/CDR timeout logs, hibern8 enter/exit cycles, and two-lane register programming.
