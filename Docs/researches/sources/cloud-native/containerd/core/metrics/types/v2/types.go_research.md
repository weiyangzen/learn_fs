# sources/cloud-native/containerd/core/metrics/types/v2/types.go

Purpose: re-exports cgroup v2 stats types under the containerd metrics package path.

Important APIs and types: aliases for `Metrics`, `MemoryStat`, `CPUStat`, `PidsStat`, and `IOStat`.

Control flow: no runtime logic; aliases allow collectors and typeurl payloads to use containerd package paths while relying on `containerd/cgroups/v3/cgroup2/stats`.

State and persistence: none.

Dependencies and integration: used by v2 collectors and tests.

Risks: public compatibility follows upstream cgroups v2 stats type shape.

Test signals: `metrics_test.go` marshals empty `v2types.Metrics` for collector regression coverage.
