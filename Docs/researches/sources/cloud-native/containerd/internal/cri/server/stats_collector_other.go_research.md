# Research: sources/cloud-native/containerd/internal/cri/server/stats_collector_other.go

This non-Linux build-tagged file provides a stub `StatsCollector` implementation so the CRI server can compile and run without Linux cgroup sampling. `NewStatsCollector` returns an empty collector, `SetDependencies` ignores the task service and store callbacks, `Start` and `Stop` are no-ops, `AddContainer` and `RemoveContainer` are no-ops, and both `GetUsageNanoCores` and `GetLatestSample` report no data.

The file preserves the same public API as the Linux implementation, allowing `service.go`, container store, sandbox store, and stats consumers to call collector methods without platform branching. There is no state, persistence, goroutine, cgroup dependency, or task metrics dependency. On Windows, sandbox stats use `sandbox_stats_windows.go` and store cached samples through container/sandbox stores rather than this background collector.

The main risk is behavior divergence: non-Linux platforms do not get background instantaneous CPU rate sampling, so callers must tolerate missing `UsageNanoCores` data. The stub intentionally prevents Linux cgroup-specific imports from leaking to other platforms. Test signal is mostly compilation across build tags and Windows stats tests; this file has no direct unit tests in the listed set.
