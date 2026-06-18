# sources/distributed-fs/ceph-client/drivers/thermal/samsung/Makefile

Purpose: Kbuild glue for Samsung thermal drivers.

Important entries: `obj-$(CONFIG_EXYNOS_THERMAL) += exynos_thermal.o` and `exynos_thermal-y := exynos_tmu.o`. This builds `exynos_tmu.c` as a composite object named `exynos_thermal`.

Control flow and integration: there are no conditional sub-objects or generated files. The composite object naming means module identity differs from the source basename but the platform driver name remains `exynos-tmu`.

State, risks, and test signals: no runtime state. Risks are limited to drift between Kconfig symbol and object names. Verify module and built-in builds and ensure the expected platform alias remains emitted by `exynos_tmu.c`.
