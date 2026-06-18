# sources/distributed-fs/ceph-client/drivers/thermal/samsung/Kconfig

Purpose: Kconfig entry for the Samsung Exynos Thermal Management Unit driver.

Important symbol: `EXYNOS_THERMAL`, a tristate option depending on `THERMAL_OF` and `HAS_IOMEM`. Its help text describes TMU initialization, temperature reporting, and cooling action via supported Exynos SoC configuration data.

Control flow and integration: enabling this symbol causes `samsung/Makefile` to build the composite `exynos_thermal` object from `exynos_tmu.o`. The `THERMAL_OF` dependency matches the driver's use of `devm_thermal_of_zone_register()`.

State and persistence: no runtime state. It controls only build inclusion.

Risks and test signals: dependency drift would surface as missing OF thermal or MMIO APIs. Test with `CONFIG_EXYNOS_THERMAL=m`, `=y`, and COMPILE_TEST-style builds where available.
