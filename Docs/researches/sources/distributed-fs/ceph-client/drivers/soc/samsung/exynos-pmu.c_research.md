# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-pmu.c

## Purpose

`exynos-pmu.c` is the generic Samsung Exynos PMU controller driver. It provides raw PMU access helpers, programs powerdown configuration tables, creates PMU regmaps, registers child devices, and implements GS101-specific CPU hotplug/cpuidle firmware hint handling.

## Important APIs, Types, and Functions

`struct exynos_pmu_context` stores device, PMU data, PMU and interrupt-generator regmaps, raw spinlock, CPU-hotplug bitmap, and suspend/reboot flags. Public helpers include `pmu_raw_writel()`, `pmu_raw_readl()`, `exynos_sys_powerdown_conf()`, `exynos_get_pmu_regmap()`, and `exynos_get_pmu_regmap_by_phandle()`. GS101 helpers manage CPU inform and interrupt bits for online/offline paths. `exynos_pmu_probe()` sets up regmap, PMU data, CPU PM integration, MFD children, and OF children.

## Control Flow

Postcore init registers the platform driver. Probe maps PMU MMIO, allocates global context, selects match data, creates either secure SMC-backed regmap or syscon regmap, initializes CPU PM state for GS101 if needed, calls optional PMU init, adds MFD cell `exynos-clkout`, and populates children. `exynos_sys_powerdown_conf()` later writes SoC powerdown tables for AFTR/LPA/SLEEP.

## State and Persistence Behavior

Global `pmu_base_addr` and `pmu_context` are singleton state. PMU register writes persist in hardware until reset or later writes. GS101 CPU PM flags persist in memory and are protected by `cpupm_lock`. Suspend/reboot notifiers gate cpuidle hint programming.

## Dependencies and Integration Points

It depends on platform MMIO, syscon/regmap, secure Tensor SMC regmap hooks, MFD, OF population, cpuhotplug, CPU PM notifiers, reboot notifiers, and SoC-specific `exynos_pmu_data`.

## Risks and Edge Cases

Singleton globals assume one PMU. CPU hotplug states and notifiers are registered without corresponding teardown in visible code, acceptable for non-removable PMU but risky for bind/unbind testing. `exynos_get_pmu_regmap_by_phandle()` calls `put_device(dev)` before returning `syscon_node_to_regmap(pmu_np)`, relying on syscon lifetime. GS101 raw spinlock paths must remain IRQ-safe and not call sleeping regmap implementations.

## Test Signals

Boot legacy Exynos and GS101, verify PMU regmap lookup by phandle, secure and syscon regmap paths, powerdown table writes for all modes, MFD child creation, CPU hotplug/cpuidle hint programming, suspend/reboot flag behavior, and no lockdep splats in CPU PM notifiers.
