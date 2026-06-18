# sources/distributed-fs/ceph-client/include/linux/arch_topology.h

## Purpose
Declares generic architecture topology interfaces for CPU capacity, frequency invariance, hardware pressure, and CPU sibling masks.

## Important APIs, Types, And Functions
Exports capacity/frequency functions such as `topology_normalize_cpu_scale()`, `topology_parse_cpu_capacity()`, `topology_set_freq_scale()`, `topology_scale_freq_invariant()`, and `topology_scale_freq_tick()`. Per-CPU variables include `capacity_freq_ref`, `arch_freq_scale`, and `hw_pressure`, with inline getters. `enum scale_freq_source` and `struct scale_freq_data` describe frequency-scale providers. `struct cpu_topology` stores thread/core/cluster/package IDs and sibling masks. Under `CONFIG_GENERIC_ARCH_TOPOLOGY`, macros expose topology IDs/masks and functions manage CPU topology lifecycle.

## Control Flow, State, And Persistence
State is held in per-CPU scale/pressure values and, when enabled, the global `cpu_topology[NR_CPUS]` table. Control flow spans boot parsing, CPU hotplug storage/removal, frequency tick updates, and scheduler-facing topology queries.

## Dependencies And Integration Points
Depends on `linux/types.h`, `linux/percpu.h`, cpumasks, OF/ACPI topology parsing, cpufreq/CPPC/virtual frequency providers, and scheduler capacity code.

## Risks And Test Signals
Wrong sibling masks or stale frequency scale values can distort scheduler placement and capacity accounting. Tests should cover DT/ACPI parsing, CPU hotplug, SMT detection through `thread_id`, frequency invariance updates, hardware pressure updates, and config fallback where `topology_core_has_smt()` is false.
