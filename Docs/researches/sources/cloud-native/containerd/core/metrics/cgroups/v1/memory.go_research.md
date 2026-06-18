# sources/cloud-native/containerd/core/metrics/cgroups/v1/memory.go

Purpose: declares the cgroup v1 memory metric set, covering memory.stat fields, hierarchical limits, usage/swap/kernel/kernel-tcp failcnt/limit/max/usage fields.

Important APIs and data: global `memoryMetrics` contains descriptors for cache, rss, mapped file, dirty/writeback, page counters/faults, active/inactive file and anon, unevictable, hierarchical limits, total variants, memory usage, swap, kernel, and kernel TCP metrics.

Control flow: each metric function checks for the relevant nested memory object before reading fields. Plain memory.stat fields check `stats.Memory`; usage/swap/kernel/kernel-tcp groups use generated getters such as `stats.GetMemory().GetUsage()` to avoid nil dereferences.

State and persistence: no state; metrics are stateless projections from cgroup v1 stats payloads into Prometheus samples.

Dependencies and integration: depends on cgroup v1 stats aliases, Docker metrics unit conventions, Prometheus gauges, and `v1.NewCollector`.

Risks: many memory.stat counters are exposed with `metrics.Bytes` even when kernel semantics are event/page counters, which is historical API behavior and hard to change. The metric list is large, so renames or unit changes are breaking for Prometheus consumers.

Test signals: no direct metric-value tests in subset; nil-safe collection is indirectly covered by empty stats in the concurrency regression test.
