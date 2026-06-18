# sources/distributed-fs/ceph-client/drivers/soc/samsung/Makefile

## Purpose

The Samsung SoC Makefile maps Exynos/Samsung Kconfig symbols to object files and multi-object modules.

## Important APIs, Types, and Functions

`exynos_chipid-y` combines `exynos-chipid.o` and `exynos-asv.o`; `exynos_pmu-y` combines `exynos-pmu.o` and `gs101-pmu.o`. ARM PMU data tables build under `CONFIG_EXYNOS_PMU_ARM_DRIVERS`. USI, regulator coupler, ASV ARM extension, and PM check objects are independently selected.

## Control Flow

Kbuild creates built-in objects or modules according to Kconfig type. Multi-object assignments ensure shared ASV and GS101 PMU code is linked with its parent module/object.

## State and Persistence Behavior

No runtime state. It controls build artifacts only.

## Dependencies and Integration Points

It depends on Kconfig symbols and local file names. Generic PMU and ChipID code depend on companion objects being linked when features are enabled.

## Risks and Edge Cases

Missing a companion object can create unresolved symbols or disabled functionality. The underscore module names (`exynos_chipid`, `exynos_pmu`) differ from source hyphen names and must match module expectations.

## Test Signals

Build each symbol combination, especially `EXYNOS_CHIPID=m`, `EXYNOS_PMU=y`, and ARM-only PMU table selections, and verify module/object contents with `nm` or build logs.
