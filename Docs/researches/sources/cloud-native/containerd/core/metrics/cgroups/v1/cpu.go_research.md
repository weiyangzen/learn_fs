# sources/cloud-native/containerd/core/metrics/cgroups/v1/cpu.go

Purpose: declares cgroup v1 CPU Prometheus metrics for total, kernel, user, per-CPU, and throttling stats.

Important APIs and data: `cpuMetrics` includes `cpu_total`, `cpu_kernel`, `cpu_user`, `per_cpu` labeled by CPU index, `cpu_throttle_periods`, `cpu_throttled_periods`, and `cpu_throttled_time`.

Control flow: each descriptor returns nil when `stats.CPU` is absent. Per-CPU usage iterates `stats.CPU.Usage.PerCPU` and labels each value with the CPU index.

State and persistence: no persistent state; descriptors are global and appended into the v1 collector.

Dependencies and integration: depends on v1 stats aliases, Docker metrics units, Prometheus gauges, and collector descriptor machinery in `metric.go`.

Risks: per-CPU metrics can create high cardinality on large hosts. CPU cumulative counters are exposed as gauge values, so consumers need to understand the cgroup stat semantics.

Test signals: no direct value tests; empty stat handling is indirectly exercised by collector regression tests.
