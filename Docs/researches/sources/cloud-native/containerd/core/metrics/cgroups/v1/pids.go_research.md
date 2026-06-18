# sources/cloud-native/containerd/core/metrics/cgroups/v1/pids.go

Purpose: declares cgroup v1 PID metrics for PID limit and current PID count.

Important APIs and data: `pidMetrics` contains two metrics named `pids`, differentiated by Docker metrics units `limit` and `current`.

Control flow: both metric functions return nil when `stats.Pids` is absent; otherwise they emit one value from `Limit` or `Current`.

State and persistence: no state; descriptors are appended to the v1 collector.

Dependencies and integration: depends on v1 stats aliases, Docker metrics units, and Prometheus gauges.

Risks: same metric name with different unit relies on Docker metrics namespace naming conventions to produce distinct final descriptors. Missing pids controller data emits no sample.

Test signals: indirectly traversed by collector tests with empty stats.
