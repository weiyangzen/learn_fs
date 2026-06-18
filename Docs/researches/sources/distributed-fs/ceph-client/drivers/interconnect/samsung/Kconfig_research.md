# sources/distributed-fs/ceph-client/drivers/interconnect/samsung/Kconfig

## Purpose

This Kconfig fragment exposes Samsung interconnect support and the generic Exynos interconnect provider. `INTERCONNECT_SAMSUNG` is the umbrella boolean for Samsung SoC interconnect drivers and is available on `ARCH_EXYNOS` or `COMPILE_TEST`. `INTERCONNECT_EXYNOS` is the tristate for the generic Exynos provider and defaults to `y` when building for Exynos.

## Important Symbols And Dependencies

`INTERCONNECT_SAMSUNG` gates the submenu-level family support. `INTERCONNECT_EXYNOS` depends on that umbrella option and controls compilation of `exynos-interconnect.o` in the local Makefile. The help text identifies supported Exynos generations such as Exynos3250, Exynos4210, Exynos4412, Exynos542x, and Exynos5433.

## Control Flow And Integration

Kconfig choice affects build inclusion only. When `INTERCONNECT_EXYNOS=y` or `m`, the Makefile builds the platform driver in `exynos.c`. The symbol also participates in distribution and randconfig coverage through `COMPILE_TEST`.

## State, Risks, And Test Signals

There is no runtime state in this file. The main risk is dependency drift: if `INTERCONNECT_EXYNOS` is enabled without required interconnect, PM QoS, OF, or platform bus support, build failures appear elsewhere; if dependency constraints are too strict, compile coverage drops. Test signals are `olddefconfig`/`randconfig` success, correct module/builtin selection for Exynos builds, and successful probe of the generic Exynos interconnect platform device when enabled.
