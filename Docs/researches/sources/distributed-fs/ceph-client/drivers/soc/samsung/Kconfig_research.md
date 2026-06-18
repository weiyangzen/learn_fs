# sources/distributed-fs/ceph-client/drivers/soc/samsung/Kconfig

## Purpose

This Kconfig file defines Samsung SoC driver support for Exynos ChipID/ASV, USI, PMU, PM suspend memory CRC checking, and the Exynos regulator coupler.

## Important APIs, Types, and Functions

`SOC_SAMSUNG` gates the menu. `EXYNOS_CHIPID` selects MFD syscon and soc bus and selects ARM ASV helpers on ARM Exynos. `EXYNOS_USI` selects syscon and defaults on for ARM64 Exynos. `EXYNOS_PMU` selects MFD core and MMIO regmap, with `EXYNOS_PMU_ARM_DRIVERS` selected for ARM Exynos. `SAMSUNG_PM_CHECK` and chunk size configure legacy suspend CRC. `EXYNOS_REGULATOR_COUPLER` enables Exynos voltage coupling.

## Control Flow

Kconfig selections drive which Makefile objects are compiled and which architecture-specific data tables are available to generic PMU and ChipID code.

## State and Persistence Behavior

No runtime state. User or defconfig choices persist in `.config`.

## Dependencies and Integration Points

It integrates with `ARCH_EXYNOS`, COMPILE_TEST, MFD, syscon, regulator, PM, CRC32, and soc bus subsystems.

## Risks and Edge Cases

Architecture gating intentionally excludes ARMv7-only data on ARM64; mismatches can produce missing PMU data pointers. `EXYNOS_PMU` is bool, not tristate, affecting init ordering. PM_CHECK options are legacy-platform-specific and can be expensive at runtime.

## Test Signals

Run ARM and ARM64 Exynos defconfigs plus COMPILE_TEST. Verify object selection for ChipID, USI, PMU core, ARM PMU tables, regulator coupler, and PM_CHECK chunk-size prompts.
