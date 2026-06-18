# sources/cloud-native/containerd/core/metrics/cgroups/v2/cpu.go

Purpose: declares cgroup v2 CPU metrics from `cpu.stat`.

Important APIs and data: `cpuMetrics` includes `cpu_usage_usec`, `cpu_user_usec`, `cpu_system_usec`, `cpu_nr_periods`, `cpu_nr_throttled`, and `cpu_throttled_usec`.

Control flow: each metric returns nil when `stats.CPU` is absent, otherwise emits one gauge value from the corresponding cgroup v2 CPU field.

State and persistence: no state; metric definitions are global data consumed by `v2.NewCollector`.

Dependencies and integration: depends on v2 stats aliases, Docker metrics units, Prometheus gauges, and v2 descriptor abstraction.

Risks: units are microseconds for usage/time fields and totals for period counters; changing names/units would break monitoring consumers. Values are cumulative gauges.

Test signals: no direct value tests; empty stats path is indirectly covered.
