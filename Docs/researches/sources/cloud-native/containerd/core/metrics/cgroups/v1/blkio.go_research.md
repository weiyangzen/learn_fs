# sources/cloud-native/containerd/core/metrics/cgroups/v1/blkio.go

Purpose: declares Prometheus metric descriptors for cgroup v1 blkio statistics and maps blkio stat entries into labeled metric values.

Important APIs and data: `blkioMetrics` contains descriptors for merged, queued, service bytes, service time, serviced, io time, and sectors recursive stats. `blkioValues` converts `[]*v1.BlkIOEntry` into `[]value` with labels `op`, `device`, `major`, and `minor`.

Control flow: each metric returns nil when `stats.Blkio` is absent, otherwise delegates to `blkioValues` for the relevant recursive slice.

State and persistence: no state; descriptors are global package variables used by the v1 collector.

Dependencies and integration: depends on cgroup v1 metrics aliases, Docker metrics units, and Prometheus value types. Integrated by `v1.NewCollector` appending `blkioMetrics`.

Risks: metric cardinality depends on blkio device entries and can grow with device count. All values are gauges, so downstream rate calculations must be done by consumers.

Test signals: no direct value tests in subset; collector concurrency test can traverse descriptors with empty stats.
