# sources/cloud-native/containerd/core/metrics/types/v1/types.go

Purpose: re-exports cgroup v1 stats protobuf/generated types under the containerd metrics package path.

Important APIs and types: aliases for `Metrics`, `BlkIOEntry`, `MemoryStat`, `CPUStat`, `CPUUsage`, `BlkIOStat`, `PidsStat`, `RdmaStat`, `RdmaEntry`, and `HugetlbStat`.

Control flow: no runtime logic; aliases allow typeurl unmarshaling and imports to refer to containerd's metrics types path while using `containerd/cgroups/v3/cgroup1/stats`.

State and persistence: none.

Dependencies and integration: used by v1 collectors and tests. Depends on `github.com/containerd/cgroups/v3/cgroup1/stats`.

Risks: type aliases couple containerd's public metrics type surface to upstream cgroups stats type names and fields.

Test signals: `metrics_test.go` creates empty `v1types.Metrics` payloads for collector regression testing.
