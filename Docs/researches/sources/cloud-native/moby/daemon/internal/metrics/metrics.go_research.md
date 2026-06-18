<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/metrics.go -->
# sources/cloud-native/moby/daemon/internal/metrics/metrics.go

Purpose: declares Docker daemon Prometheus/go-metrics instruments and a custom collector for container state counts.

Important APIs and types: package variables such as `ContainerActions`, `NetworkActions`, `HostInfoFunctions`, `ImageActions`, `EngineInfo`, `EngineCPUs`, `EngineMemory`, health check counters/timers, `StateCtr`, event metrics, `StartTimer`, and `StateCounter`.

Control flow: `init` preinitializes selected container action labels to zero and registers the namespace. `StateCounter` stores container ID to state label mappings; `Collect` emits running/paused/stopped gauges.

State and persistence: metrics are process-global. `StateCounter` protects its map with an RW mutex and has no disk persistence.

Dependencies and integration: depends on `docker/go-metrics` and Prometheus. Used throughout daemon operations to expose engine metrics.

Risks: state labels are stringly typed and only three labels are counted. Global registration in `init` can complicate tests or multiple daemon instances in one process.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/metrics.go -->
