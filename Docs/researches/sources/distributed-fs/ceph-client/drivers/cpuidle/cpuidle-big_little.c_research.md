# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-big_little.c

Purpose: registers separate ARM big and LITTLE cpuidle drivers for MCPM-based Cortex-A15/A7 systems such as Versatile Express TC2 and Google Peach.

Important APIs and functions: `bl_powerdown_finisher()` programs the MCPM entry vector and calls `mcpm_cpu_suspend()` from a notrace suspend finisher. `bl_enter_powerdown()` wraps `cpu_suspend()` with `cpu_pm_enter/exit`, `ct_cpuidle_enter/exit`, and `mcpm_cpu_powered_up()`. `bl_idle_driver_init()` builds driver cpumasks by CPU part ID. `bl_idle_init()` verifies machine compatibility and MCPM availability, parses DT idle states at index 1, and registers LITTLE then big drivers.

Control flow and state: two static driver templates define WFI plus a powerdown C1 state, with different default latency/residency values for A7 and A15. Runtime state is limited to allocated cpumasks assigned to each driver.

Dependencies and integration points: depends on MCPM, ARM suspend, CPU part ID helpers, DT `arm,idle-state`, and CPU PM/RCU idle context tracking.

Risks and test signals: risks include hard-coded Cortex-A7/A15 part differentiation, cpumask leaks on full success because there is no remove path, reliance on platform-specific MCPM back ends for cluster shutdown policy, and default latency values being platform-specific. Test signals include machine compatible gating, cpumasks containing only matching cores, DT override of state data, successful CPU suspend/resume through MCPM, and rollback freeing cpumasks on registration failure.
