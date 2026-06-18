# sources/cloud-native/containerd/core/metrics/cgroups/v2/pids.go

Purpose: declares cgroup v2 PID metrics for PID limit and current PID count.

Important APIs and data: `pidMetrics` contains two `pids` descriptors differentiated by units `limit` and `current`, with cgroup v2-specific help text.

Control flow: both functions return nil when `stats.Pids` is absent, otherwise emit one gauge from `Limit` or `Current`.

State and persistence: no state; descriptors are consumed by the v2 collector.

Dependencies and integration: depends on v2 stats aliases, Docker metrics units, and Prometheus.

Risks: same final-name/unit convention as v1 applies. Missing pids stats emit no sample.

Test signals: indirectly exercised by empty stats collector tests.
