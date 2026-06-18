# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/collector/snapshotter.go

This file collects resource metrics for the snapshotter process and cache directory. `SnapshotterMetricsCollector` stores context, cache path, PID, and the last process stat sample. Snapshot methods are enumerated for operation latency labels.

`CollectCacheUsage` runs `continuity/fs.DiskUsage` and reports kilobytes. `CollectResourceUsage` samples `/proc` through `metrics/tool`, computes CPU system/user deltas, CPU percent, memory RSS, fd count, runtime, and thread count, then updates gauges. `Collect` runs both cache and resource collection. `CollectSnapshotMetricsTimer` creates a Prometheus timer that writes elapsed milliseconds to the snapshot operation histogram.

State is the rolling `lastStat` baseline and Prometheus metric values. Integration points include `metrics.Server`, manager cache directories, snapshotter operation instrumentation, and `/proc`. Risks include failed stat reads, CPU percent division by zero if uptime delta is zero, resource units depending on global `ClkTck` and page size, and disk usage cost on large cache directories. There are no direct tests for this collector in the subset.
