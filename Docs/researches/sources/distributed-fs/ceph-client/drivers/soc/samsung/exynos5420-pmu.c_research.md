# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos5420-pmu.c

## Purpose

`exynos5420-pmu.c` supplies the Exynos5420/5422 PMU policy table and initialization hooks used by the common Samsung Exynos PMU driver. It describes how major CPU, clock, memory, pad-retention, and IP power domains should be programmed for AFTR, LPA, and SLEEP modes, then performs chip-specific one-time PMU setup.

## Important APIs, Types, and Functions

The main data object is `exynos5420_pmu_config[]`, an array of `struct exynos_pmu_conf` entries ending with `PMU_TABLE_END`. Each entry maps a PMU register offset from `exynos-regs-pmu.h` to three mode values. `exynos5420_list_disable_pmu_reg[]` lists local CMU clock-stop, sysclk, and reset PMU registers that must be cleared initially. `exynos5420_powerdown_conf()` writes the current CPU cluster id to `EXYNOS_IROM_DATA2`. `exynos5420_pmu_init()` applies low-level workaround/configuration writes. `exynos5420_pmu_data` exports the table and callbacks to the common PMU layer.

## Control Flow

During PMU driver setup, the common Exynos PMU code consumes `exynos5420_pmu_data`, iterates `pmu_config` when entering system power states, and calls `pmu_init`. Initialization clears selected local-power CMU entries, enables standby-WFI for all cores, disables L2 retention bits for both clusters, masks LPI paths for ISP/KFC ATB bridges, sets ACE/ACP deactivation skip bits for ARM and KFC common blocks, programs reset-duration and interrupt-spread registers, and enables the upstream scheduler. Before powerdown, `powerdown_conf` records the current cluster from MPIDR affinity level 1 so resume returns through the expected cluster.

## State and Persistence Behavior

The file has no heap state or file-backed persistence. Its static tables are immutable kernel data. Persistent effects are MMIO writes into PMU registers that survive across suspend/resume according to SoC reset and retention rules. `EXYNOS_IROM_DATA2` is used as firmware-visible scratch state for wakeup routing.

## Dependencies and Integration Points

It depends on the Exynos PMU core, raw PMU accessors (`pmu_raw_readl`, `pmu_raw_writel`), ARM MPIDR helpers, and SoC register definitions. It integrates with Samsung suspend/resume code through `struct exynos_pmu_data`.

## Risks and Edge Cases

The configuration is register-table driven; wrong offsets or mode columns can silently break suspend, clocks, or retention. `exynos5420_powerdown_conf()` assumes affinity level 1 maps directly to the cluster id expected by IROM. The L2 retention and LPI mask workarounds are hardware-specific and risky to generalize. The initial clearing loop has no readback or error path, so validation depends on hardware behavior.

## Test Signals

Useful signals are boot logs showing PMU initialization, suspend/resume across AFTR/LPA/SLEEP, wakeup from both ARM and KFC clusters, no LPI hang when ISP-related clocks are gated, and no regression in CPU hotplug or cluster powerdown. Build coverage should include `CONFIG_SOC_EXYNOS5420` paths and register-definition drift.
