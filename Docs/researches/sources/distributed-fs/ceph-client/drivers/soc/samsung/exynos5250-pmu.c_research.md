# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5250-pmu.c

## Purpose

`exynos5250-pmu.c` supplies Exynos5250 PMU low-power configuration and initialization callbacks. It prepares watchdog reset behavior and option-register settings for system powerdown modes.

## Important APIs, Types, and Functions

`exynos5250_pmu_config[]` lists AFTR/LPA/SLEEP register values. `exynos5_list_both_cnt_feed[]` names option registers that should use both SC feedback and counters. `exynos5_list_disable_wfi_wfe[]` names option registers whose standby WFI/WFE bits are cleared. `exynos5250_pmu_init()` unmasks watchdog reset requests. `exynos5_powerdown_conf()` applies option-register updates before table writes. `exynos5250_pmu_data` exports the config.

## Control Flow

Generic PMU probe invokes `pmu_init()`. On powerdown configuration, `exynos_sys_powerdown_conf()` first calls `powerdown_conf()`, then iterates the PMU table for the requested mode.

## State and Persistence Behavior

All state changes are PMU register writes. Static arrays are immutable. No driver-private state is stored.

## Dependencies and Integration Points

It depends on Exynos5 PMU register definitions and the generic PMU framework. It is compiled as ARM PMU data.

## Risks and Edge Cases

Watchdog reset unmasking is critical for system recovery. Option-register updates affect CPU and peripheral low-power entry; incorrect bits can break suspend/resume. Table termination and mode-column alignment are required for safe iteration.

## Test Signals

Validate watchdog reset behavior, AFTR/LPA/SLEEP entry and resume, option-register values after `powerdown_conf()`, and PMU table writes against hardware documentation.
