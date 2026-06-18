# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos3250-pmu.c

## Purpose

`exynos3250-pmu.c` supplies Exynos3250 PMU powerdown tables and initialization callbacks to the generic Exynos PMU driver.

## Important APIs, Types, and Functions

`exynos3250_pmu_config[]` lists PMU register values for AFTR, W-AFTR/LPA, and sleep modes, terminated by `PMU_TABLE_END`. `exynos3250_powerdown_conf_extra()` configures SC feedback/counters and sleep durations. `exynos3250_pmu_init()` sets ACE/ACP behavior, standby WFI, and PSHOLD output/enables. `exynos3250_pmu_data` exports the table and callbacks.

## Control Flow

Generic PMU probe calls `pmu_init()`. Later `exynos_sys_powerdown_conf()` writes the main table and invokes the extra callback for the selected powerdown mode.

## State and Persistence Behavior

No private state exists. Calls write PMU registers through `pmu_raw_readl/writel`; those settings persist in PMU hardware until reset or subsequent power-management writes.

## Dependencies and Integration Points

It depends on Exynos PMU register definitions and the generic PMU data contract in `exynos-pmu.h`. It is built only when ARM PMU driver data is enabled.

## Risks and Edge Cases

Table ordering and mode columns must match `enum sys_powerdown`. Missing terminator would overrun in generic code. PSHOLD and standby settings are board-critical and should not be changed casually.

## Test Signals

Boot Exynos3250, verify PMU init register effects, exercise AFTR/W-AFTR/SLEEP table writes, confirm durations in sleep mode, and validate suspend/resume and power-off behavior.
