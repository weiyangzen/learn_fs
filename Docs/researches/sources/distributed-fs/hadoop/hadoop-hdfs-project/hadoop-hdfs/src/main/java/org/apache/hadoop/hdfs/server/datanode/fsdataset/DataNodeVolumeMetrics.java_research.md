# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/DataNodeVolumeMetrics.java

Purpose: maintains per-DataNode-volume IO metrics and publishes them through Hadoop Metrics2 as the `DataNodeVolume` source. It records metadata operation latency, data file IO latency, flush/sync/read/write/transfer/native-copy latency, and file IO error latency.

Important APIs/types/functions: `create(Configuration, String)` registers a metrics source in `DefaultMetricsSystem` with a sanitized volume name; `unRegister()` removes it. `getVolumeName()` exposes a tag by stripping `DataNodeVolume-` or `UndefinedDataNodeVolume` prefixes. `add*Latency` methods update `MutableRate` instances and optional `MutableQuantiles`; `addMetadataOperationLatency`, `addDataFileIoLatency`, and `addFileIoError` also increment counters. Getter methods expose last interval sample counts, mean, stddev, total counters, and selected quantile arrays.

Control flow: construction allocates one `MutableQuantiles` array per configured percentile interval. `create` reads `DFS_METRICS_PERCENTILES_INTERVALS_KEY`; if no intervals are configured, percentile arrays are zero length and update loops are no-ops. Each update path performs a counter/rate update and then appends the latency to every quantile bucket for that operation.

State and persistence: all state is in-memory Metrics2 mutable counters/rates/quantiles. There is no on-disk persistence. Metrics source naming must be unique; empty volume names receive an `UndefinedDataNodeVolume` random suffix.

Dependencies and integration points: depends on Metrics2 annotations, `MetricsRegistry`, `MutableRate`, `MutableCounterLong`, `MutableQuantiles`, `DFSConfigKeys`, and `ThreadLocalRandom`. It is exposed through `FsVolumeSpi.getMetrics()` and is updated by volume/file IO code through `FileIoProvider` and dataset operations.

Risks: `getVolumeName()` recompiles a regex on every call. Last-stat getters depend on Metrics2 snapshot behavior, so tests must trigger metric snapshots if asserting values. Duplicate sanitized names can collide if two non-empty volume names differ only by colon replacement. Quantile overhead grows with configured interval count.

Test signals: verify source registration/unregistration, empty-name uniqueness, counter/rate increments after `add*Latency`, no failure when percentile intervals are empty, and expected quantile additions when intervals are configured.
