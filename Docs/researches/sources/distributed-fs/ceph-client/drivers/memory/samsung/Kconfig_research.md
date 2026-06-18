# sources/distributed-fs/ceph-client/drivers/memory/samsung/Kconfig

Purpose: Kconfig menu for Samsung Exynos memory-controller drivers. It gates the Exynos5422 Dynamic Memory Controller DVFS driver and the Exynos SROM controller driver under a top-level `SAMSUNG_MC` option.

Important APIs/types/functions: configuration symbols are `SAMSUNG_MC`, `EXYNOS5422_DMC`, and `EXYNOS_SROM`. `EXYNOS5422_DMC` selects `DDR`, depends on Exynos or compile-test I/O support, simple ondemand devfreq governor, `PM_DEVFREQ`, and `PM_DEVFREQ_EVENT`. `EXYNOS_SROM` depends on ARM Exynos or compile-test I/O support.

Control flow: enabling `SAMSUNG_MC` exposes the two child options. The DMC option permits building `exynos5422-dmc.o` as built-in or module. The SROM option is boolean and builds `exynos-srom.o` when selected.

State and persistence: no runtime state. The file controls build-time availability and dependency closure for runtime drivers.

Dependencies and integration: integrates with `drivers/memory/samsung/Makefile` and kernel subsystems needed by the drivers: DDR timing helpers, devfreq, devfreq-event, regulators, clocks, and platform MMIO.

Risks: missing devfreq or DDR dependencies would produce compile or link failures in `exynos5422-dmc.c`. Making SROM modular would conflict with its `builtin_platform_driver()` use. The `COMPILE_TEST` branches are important for cross-architecture build coverage.

Test signals: run Kconfig combinations for `ARCH_EXYNOS`, `COMPILE_TEST`, devfreq disabled, and SROM-only builds; confirm the Makefile selects only the intended objects.
