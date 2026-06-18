# sources/cloud-native/containerd/core/metrics/cgroups/v1/metrics.go

Purpose: implements the cgroup v1 Prometheus collector that tracks stat-capable tasks and emits all configured v1 metrics.

Important APIs and types: `Trigger`, `NewCollector`, `taskID`, `entry`, `Collector`, and methods `Describe`, `Collect`, `collect`, `Add`, `Remove`, and `RemoveAll`.

Control flow: `NewCollector` returns an inert collector when namespace is nil; otherwise it appends pids, CPU, memory, hugetlb, and blkio metric definitions, allocates a stored metric channel, and registers with the namespace. `Collect` holds a read lock while spawning one goroutine per task to collect stats and flushing stored metrics, releases the lock, then waits for goroutines. `collect` calls task `Stats` with a namespace-aware timeout context, unmarshals into v1 metrics, chooses a child namespace with const labels if configured, and emits every metric. `Add` checks idempotently under a read lock, creates child const labels outside the write lock, then stores the entry. `Remove` and `RemoveAll` mutate the task map.

State and persistence: runtime-only task map keyed by `id-namespace`, metric definitions, and stored metrics channel. No persistent state.

Dependencies and integration: uses common `Statable`, cgroup v1 type aliases, typeurl, timeout setting from core metrics, namespace context, Docker metrics, Prometheus, and logging.

Risks: comments document historical deadlock risk with namespace locks and collector locks. Collection spawns goroutines while holding a read lock until stored metrics are flushed; slow task stats can still consume resources. Errors are logged and metrics for that task are skipped.

Test signals: `metrics_test.go` directly validates concurrent `Add` and namespace `Collect` do not deadlock.
