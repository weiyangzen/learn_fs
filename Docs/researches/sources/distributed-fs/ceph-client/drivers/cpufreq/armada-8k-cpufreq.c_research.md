# sources/distributed-fs/ceph-client/drivers/cpufreq/armada-8k-cpufreq.c

## Purpose

This Armada 8K helper synthesizes OPP tables from CPU clock rates and registers `cpufreq-dt`. It supports Marvell AP806/AP807 CPU clock compatibles and assumes valid operating points are the nominal clock divided by 1, 2, 3, and 4.

## Important APIs, types, and functions

`opps_div[]` defines the synthetic dividers. `struct freq_table` tracks each CPU device and dynamically added frequencies so exit/error paths can remove them. `armada_8k_get_sharing_cpus()` groups CPUs sharing the same clock, `armada_8k_add_opp()` adds per-cluster OPPs, `armada_8k_cpufreq_free_table()` cleans them up, and `armada_8k_cpufreq_init()` performs discovery and `cpufreq-dt` platform-device registration.

## Control flow, state, and persistence

Module init checks for an available matching CPU clock node, allocates a table sized by possible CPUs, and iterates a cpumask of unprocessed CPUs. For each cluster representative, it gets the CPU clock, adds four OPPs based on the current clock rate, identifies all CPUs sharing that clock, marks OPP sharing, removes those CPUs from the work mask, and finally registers a `cpufreq-dt` platform device. State is dynamic OPP entries, sharing masks in OPP core, and the registered platform device; exit unregisters the device and removes tracked OPPs.

## Dependencies and integration points

The driver depends on OF CPU clock nodes, the common clock framework, OPP core, cpumask topology, and `cpufreq-dt`. It is a setup layer rather than the runtime cpufreq policy implementation.

## Risks and test signals

Risks include assuming only integer divider OPPs are valid, treating current boot rate as nominal maximum, incomplete cleanup if OPP addition fails mid-cluster, and bad sharing masks if clock providers do not compare as expected. Test by booting AP806/AP807 systems, checking dynamic OPP tables per cluster, validating `cpufreq-dt` registration, switching through all divider rates, and unloading if modular to confirm OPP cleanup.
