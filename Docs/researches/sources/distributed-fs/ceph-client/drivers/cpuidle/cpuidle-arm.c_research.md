# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-arm.c

Purpose: generic ARM/ARM64 DT-based cpuidle driver. It registers a per-CPU cpuidle driver with architectural WFI plus DT-described idle states that enter through ARM CPU operations.

Important APIs and functions: `arm_enter_idle_state()` calls `CPU_PM_CPU_IDLE_ENTER(arm_cpuidle_suspend, idx)`. `arm_idle_init_cpu()` duplicates the template driver, sets `drv->cpumask` to one CPU, parses DT idle states starting at index 1 with `dt_init_idle_driver()`, calls `arm_cpuidle_init(cpu)`, registers the driver, and registers cpuidle cooling. `arm_idle_init()` iterates present CPUs and rolls back previously registered drivers on failure.

Control flow and state: the template driver contains state 0 WFI. Per-CPU driver allocations are heap objects retained by cpuidle until unregister. DT idle states must exist beyond WFI or init fails with `-ENODEV`.

Dependencies and integration points: depends on `arm,idle-state` DT nodes, arch `arm_cpuidle_suspend/init`, CPU PM wrappers, cpuidle cooling, and device initcall ordering after CPU devices exist.

Risks and test signals: risks include all-present-CPU rollback freeing drivers only for CPUs before the failure point, `-ENXIO` treated as nonfatal but still no driver for that CPU, no runtime remove path, and DT-only behavior refusing WFI-only systems. Test signals include parsed DT state count, per-CPU cpumasks, arch backend init success or acceptable `-EOPNOTSUPP`, cpuidle cooling registration, and idle state entry reaching the platform CPU ops suspend path.
