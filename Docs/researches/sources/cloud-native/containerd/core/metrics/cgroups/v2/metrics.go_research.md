# sources/cloud-native/containerd/core/metrics/cgroups/v2/metrics.go

Purpose: implements the cgroup v2 Prometheus collector that tracks stat-capable tasks and emits configured v2 metrics.

Important APIs and types: `NewCollector`, `taskID`, `entry`, `Collector`, and methods `Describe`, `Collect`, `collect`, `Add`, `Remove`, and `RemoveAll`.

Control flow: `NewCollector` builds an inert collector for nil namespace or registers a collector with pids, CPU, memory, and IO metrics. `Collect` read-locks the task map, spawns one goroutine per task to collect stats, flushes stored metrics, unlocks, then waits. `collect` calls task stats with a namespaced timeout context, unmarshals into v2 metrics, chooses optional const-label namespace, and emits each metric. `Add` is idempotent and creates child namespaces with labels outside the write lock. Remove operations mutate the task map.

State and persistence: runtime-only collector fields: namespace, stored metrics channel, task map, metric definitions, and mutex.

Dependencies and integration: depends on common `Statable`, v2 stats aliases, typeurl, timeout setting, namespace context, Docker metrics, Prometheus, and logging.

Risks: same lock-ordering concerns as v1 are documented. Slow or stuck task stats are bounded by `ShimStatsRequestTimeout`, but many tasks can still spawn many goroutines during collection.

Test signals: `metrics_test.go` covers concurrent `Add` and namespace collection on cgroup v2 hosts.
