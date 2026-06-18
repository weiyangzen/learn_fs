# sources/distributed-fs/ceph-client/drivers/base/arch_topology.c

## Purpose
Provides common architecture CPU topology, capacity, frequency-invariance, hardware-pressure, and sibling-mask support. It parses CPU topology from DT or ACPI, initializes scheduler capacity values, tracks frequency scale sources, and exposes masks used by scheduler domain construction.

## Important APIs, Types, And Functions
- Frequency invariance: `topology_set_scale_freq_source()`, `topology_clear_scale_freq_source()`, `topology_scale_freq_tick()`, `topology_set_freq_scale()`, and `topology_scale_freq_invariant()`.
- Capacity/hardware pressure: `capacity_freq_ref`, `arch_freq_scale`, `hw_pressure`, `topology_update_hw_pressure()`, `topology_parse_cpu_capacity()`, and `topology_normalize_cpu_scale()`.
- Topology parsing and masks: `parse_dt_topology()`, `parse_acpi_topology()`, `init_cpu_topology()`, `store_cpu_topology()`, `update_siblings_masks()`, `cpu_coregroup_mask()`, and `cpu_clustergroup_mask()`.

## Control Flow
Early topology init resets all CPU topology entries, parses ACPI PPTT where available, otherwise parses DT `/cpus/cpu-map`, normalizes capacity when raw capacity and frequency references are known, and fetches early cache info. CPU bring-up calls `store_cpu_topology()` to fill fallbacks and update sibling masks. Cpufreq notifier completion can normalize DT capacities later and rebuild scheduler domains.

## State And Persistence
Persistent state includes global `cpu_topology[]`, per-CPU capacity/frequency/hardware-pressure variables, RCU-protected per-CPU scale-frequency data pointers, raw capacity during initialization, SMT thread count, and cpumasks for counter-backed frequency invariance.

## Dependencies And Integration Points
Integrates with scheduler topology and energy model rebuilds, cpufreq notifiers, ACPI CPPC/PPTT, OF CPU maps, cacheinfo, cpuset/cpumasks, CPU SMT control, RCU, workqueues, and trace events for hardware pressure.

## Risks And Edge Cases
Partial or inconsistent CPU capacity data is discarded and falls back to uniform capacity. Nested clusters beyond a flat cluster list are warned as unsupported. Frequency invariance source changes require careful RCU synchronization to avoid use-after-free. ACPI/DT parsing errors reset topology to avoid partial scheduler state.

## Test Signals
DT cpu-map with sockets/clusters/cores/threads, ACPI PPTT threaded/non-threaded CPUs, missing capacity properties, cpufreq policy creation order, counter-backed frequency scale registration/removal, CPU hotplug sibling mask updates, LLC sharing, and hardware pressure trace updates are key signals.
