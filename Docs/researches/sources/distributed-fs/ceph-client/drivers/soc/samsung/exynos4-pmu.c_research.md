# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos4-pmu.c

## Purpose

`exynos4-pmu.c` provides PMU powerdown configuration tables for Exynos4210, Exynos4212, and Exynos4412 to the generic Exynos PMU driver.

## Important APIs, Types, and Functions

`exynos4210_pmu_config[]` covers Exynos4210 low-power registers. `exynos4x12_pmu_config[]` covers Exynos4212/4412 baseline registers. `exynos4412_pmu_config[]` adds core 2/3 entries for quad-core Exynos4412. Exported `exynos4210_pmu_data`, `exynos4212_pmu_data`, and `exynos4412_pmu_data` reference these tables.

## Control Flow

Generic PMU match data selects the relevant `exynos_pmu_data`. When entering a system powerdown mode, `exynos_sys_powerdown_conf()` iterates the primary table and then optional extra table for Exynos4412.

## State and Persistence Behavior

The file contains static configuration data only. Runtime state is PMU hardware register contents after generic table writes.

## Dependencies and Integration Points

It depends on Exynos PMU register definitions and generic PMU table iteration. It is ARM-only PMU data selected by Kconfig.

## Risks and Edge Cases

Mode-value columns must align with AFTR, LPA, and SLEEP. Exynos4412 requires both baseline and extra tables; missing the extra table would skip cores 2/3. Hardware register definitions must match the SoC revision.

## Test Signals

Suspend/resume tests on Exynos4210, 4212, and 4412; verify table terminators; inspect PMU writes for each powerdown mode; and validate quad-core CPU retention/powerdown behavior on 4412.
