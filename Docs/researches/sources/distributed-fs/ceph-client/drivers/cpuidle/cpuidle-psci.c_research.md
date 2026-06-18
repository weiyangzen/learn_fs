# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci.c

Purpose: implements the ARM PSCI cpuidle driver, parsing DT idle states into PSCI suspend parameters and optionally integrating hierarchical CPU power domains for OSI-mode shared states.

Important APIs and functions: `psci_enter_idle_state()` enters a per-CPU PSCI state through `CPU_PM_CPU_IDLE_ENTER_PARAM_RCU(psci_cpu_suspend_enter, ...)`. Domain-aware entry `__psci_enter_domain_idle_state()` wraps CPU PM, genpd runtime/system suspend, optional domain state override, PSCI suspend, tracepoints, rejection accounting, and domain state cleanup. `psci_dt_parse_state_node()` validates `arm,psci-suspend-param`. `psci_idle_init_cpu()` checks CPU enable-method `psci`, allocates a per-CPU driver with WFI state 0, parses DT idle states, initializes per-CPU PSCI state arrays/topology, registers cpuidle, and registers cooling.

Control flow and state: per-CPU `psci_cpuidle_data` stores the PSCI state array and optional attached PM-domain device. Per-CPU `psci_domain_state` carries the domain-selected state for the next idle entry. Global `psci_cpuidle_use_syscore` triggers syscore suspend/resume handling. A faux device owns devm allocations for all per-CPU driver setup.

Dependencies and integration points: depends on DT `arm,idle-state` nodes, CPU `enable-method = "psci"`, initialized `psci_ops.cpu_suspend`, PSCI power-state validation, DT idle genpd attachment, genpd runtime PM, CPU hotplug, syscore ops, trace events, and cpuidle cooling.

Risks and test signals: risks include hierarchical topology limited to OSI, deepest CPU state being reused to trigger domain selection, global syscore flag reset in per-CPU deinit, rollback assuming previous CPUs have registered cpuidle devices, runtime PM differences on PREEMPT_RT, and failure if any present CPU lacks matching PSCI idle states. Test signals include DT suspend params logged, invalid params rejected, per-CPU drivers registered with WFI plus DT states, genpd attached devices for OSI topology, trace_psci_domain_idle events, CPU hotplug PM runtime get/put balance, and domain rejection counters incrementing on failed suspend.
