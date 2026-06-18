<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-riscv-sbi.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-riscv-sbi.c

## Purpose

`cpuidle-riscv-sbi.c` is the RISC-V SBI HSM cpuidle backend. It converts CPU idle-state device-tree nodes into per-HART `cpuidle_driver` instances, maps each state to an SBI suspend parameter, and optionally models hierarchical CPU power domains through genpd when SBI OSI-style topology data is present.

## Important APIs, Types, And Functions

The central per-CPU state is `struct sbi_cpuidle_data`, holding the parsed SBI states and optional attached PM-domain device. `struct sbi_domain_state` carries a selected domain-level suspend parameter from genpd `power_off`. `sbi_cpuidle_enter_state()` calls `riscv_sbi_hart_suspend()` directly, while `sbi_enter_domain_idle_state()` and `sbi_enter_s2idle_domain_idle_state()` wrap runtime PM/genpd and CPU PM around domain-aware suspend. `sbi_dt_parse_state_node()`, `sbi_cpuidle_dt_init_states()`, `sbi_cpuidle_init_cpu()`, `sbi_pd_init()`, and `sbi_genpd_probe()` perform DT parsing and registration.

## Control Flow

`arch_initcall()` registers a synthetic `sbi-cpuidle` platform device only if SBI HSM is supported. Probe first detects whether all CPU nodes provide named `power-domains`, then builds `/cpus/power-domains` providers, initializes each present CPU's driver, and installs CPU hotplug callbacks if any CPU was attached to a PM domain. For each CPU, state 0 is architectural WFI, DT states start at index 1, and the deepest state is replaced by the domain-aware enter callback when OSI topology is attached.

## State And Persistence Behavior

Per-CPU parsed state arrays are devm-managed. Runtime PM references keep attached CPU PM-domain devices active while CPUs are online. Domain state is intentionally cleared after idle exit and CPU hotplug down so stale genpd choices cannot leak into the next suspend attempt.

## Dependencies And Integration Points

It depends on RISC-V SBI HSM, RISC-V suspend validation, DT idle-state bindings, genpd, CPU PM, runtime PM, CPU hotplug, cpuidle cooling, and the cpuidle core. The `riscv,sbi-suspend-param` property is the firmware ABI.

## Risks And Test Signals

Risks include invalid SBI suspend parameters, partial CPU topology causing OSI mode to be disabled, failure unwinds that unregister per-CPU drivers, and genpd provider cleanup leaving stale domains. Test by booting RISC-V DTs with and without `/cpus/power-domains`, checking cpuidle states and cooling registration, CPU hotplugging, entering s2idle, and tracing SBI suspend parameters selected for CPU and domain states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-riscv-sbi.c -->
