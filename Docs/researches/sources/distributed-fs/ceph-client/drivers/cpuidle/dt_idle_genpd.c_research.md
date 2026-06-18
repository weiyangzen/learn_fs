<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.c

## Purpose

`dt_idle_genpd.c` provides reusable helpers for cpuidle drivers that model CPU idle topology with generic PM domains. It parses domain idle states, allocates `generic_pm_domain` objects, wires parent/child domain topology, and attaches CPU devices to named domains.

## Important APIs, Types, And Functions

`dt_idle_pd_alloc()` allocates a PM domain, names it from the DT node, parses genpd idle states with `of_genpd_parse_idle_states()`, and stores driver-specific state data via a caller-provided parser. `dt_idle_pd_free()` frees state data and the domain. `dt_idle_pd_init_topology()` and `dt_idle_pd_remove_topology()` add/remove subdomains from child `power-domains` links. `dt_idle_attach_cpu()` and `dt_idle_detach_cpu()` bind CPUs to named PM domains.

## Control Flow

Allocation parses each domain-idle-state node, allocates a `u32` data payload per state, and stores it in `genpd_power_state.data`. Topology init scans children under a CPU power-domain container, finds nodes with parent domains, and calls genpd add-subdomain APIs. CPU attachment marks the attached PM-domain device IRQ-safe, runtime-resumes it if the CPU is online, and marks it as a syscore device.

## State And Persistence Behavior

Domain state arrays and per-state data persist until `dt_idle_pd_free()`. Attached CPU devices hold runtime PM references while online. The code does not own provider registration; callers must call genpd provider APIs and cleanup consistently.

## Dependencies And Integration Points

It depends on OF genpd parsing, generic PM domains, runtime PM, CPU devices, DT `power-domains` links, and cpuidle platform drivers such as RISC-V SBI.

## Risks And Test Signals

Risks include memory leaks on partial parse failure, mismatched topology add/remove ordering, CPU devices left attached, and bad parser callbacks accepting invalid firmware states. Test by injecting malformed domain idle states, validating genpd topology, CPU hotplugging, and checking runtime PM references after driver teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.c -->
