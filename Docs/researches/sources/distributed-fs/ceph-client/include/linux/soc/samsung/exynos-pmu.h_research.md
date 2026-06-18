# sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-pmu.h

Purpose: This header exposes Exynos PMU helpers for system powerdown configuration and PMU regmap access.

Important APIs/types/functions: It defines `enum sys_powerdown` values `SYS_AFTR`, `SYS_LPA`, `SYS_SLEEP`, and `NUM_SYS_POWERDOWN`, declares `exynos_sys_powerdown_conf`, and conditionally declares `exynos_get_pmu_regmap` and `exynos_get_pmu_regmap_by_phandle`. Disabled stubs return `ERR_PTR(-ENODEV)`.

Control flow: Power-management code configures the selected system powerdown mode before suspend. Drivers needing PMU registers obtain the global or phandle-selected PMU regmap.

State and persistence: PMU registers hold low-power mode, wake, retention, and PHY control state. Regmap handles are provider-owned.

Dependencies and integration: Uses regmap and device tree nodes. Integrates with Exynos suspend/resume, PHY, clock, reset, and power-domain drivers.

Risks and test signals: Wrong mode configuration can prevent suspend or resume. Test disabled PMU configs, regmap lookup by phandle, AFTR/LPA/SLEEP transitions, wakeup sources, and PHY control users.
