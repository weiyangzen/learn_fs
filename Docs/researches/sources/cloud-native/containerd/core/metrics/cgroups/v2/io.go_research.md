# sources/cloud-native/containerd/core/metrics/cgroups/v2/io.go

Purpose: declares cgroup v2 IO metrics from per-device IO usage entries.

Important APIs and data: `ioMetrics` includes `io_rbytes`, `io_wbytes`, `io_rios`, and `io_wios`, all labeled by `major` and `minor`.

Control flow: metric functions return nil when `stats.Io` is absent, otherwise iterate `stats.Io.Usage` and emit one value per device.

State and persistence: no state; descriptors are consumed by the v2 collector.

Dependencies and integration: depends on v2 stats aliases, Docker metrics units, Prometheus, and strconv label conversion.

Risks: device-level labels can create cardinality proportional to block devices. Only read/write bytes and IO counts are exported here, not all possible cgroup v2 IO stats.

Test signals: no direct tests in subset.
