# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-cps.c

Purpose: implements MIPS CPS cpuidle states: coherent wait, non-coherent wait, core clock gating, and core power gating, adapting the available state count to CPS PM support.

Important APIs and functions: `cps_nc_enter()` maps the selected cpuidle index to `enum cps_pm_state`, prevents deeper-than-noncoherent states for CPUs sibling to core 0, wraps power-gated entry in `cpu_pm_enter/exit`, and calls `cps_pm_enter_state()`. `cps_cpuidle_init()` trims state count based on `cps_pm_support_state()`, marks states coupled when `coupled_coherence` requires it, registers the driver, initializes each per-CPU `cpuidle_dev`, optionally sets `coupled_cpus`, and registers devices.

Control flow and state: per-CPU devices live in `per_cpu(cpuidle_dev)`. Driver state count is reduced from deepest to shallowest depending on hardware. Error cleanup unregisters all possible CPU devices and the driver.

Dependencies and integration points: depends on MIPS idle macros, CPS PM support, optional `ARCH_NEEDS_CPU_IDLE_COUPLED`, `cpu_sibling_map`, and CPU PM notifiers for power-gated states.

Risks and test signals: risks include special casing core 0 rather than dynamically ensuring one core remains alive, BUG on invalid index, coupled-state correctness relying on external `coupled_coherence`, and static per-CPU device registration for all possible CPUs. Test signals include boot log limited-state messages, state flags gaining `CPUIDLE_FLAG_COUPLED` on affected systems, successful cpuidle device registration per CPU, and correct refusal to power-gate the last essential sibling.
