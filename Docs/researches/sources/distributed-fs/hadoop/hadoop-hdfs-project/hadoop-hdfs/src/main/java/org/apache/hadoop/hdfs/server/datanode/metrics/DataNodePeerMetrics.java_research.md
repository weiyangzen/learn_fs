# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodePeerMetrics.java

## Purpose

`DataNodePeerMetrics` records downstream packet-send latency by peer DataNode and identifies slow peers using rolling averages and `OutlierDetector`. It supports DataNode slow-peer reporting.

## Important APIs, Control Flow, and State

The constructor reads minimum samples, low threshold, and minimum node count from configuration, creates an `OutlierDetector`, and initializes a `MutableRollingAverages` named `Time`. `create` builds a metrics source name from the DataNode name. `addSendPacketDownstream` records elapsed time for a peer address. `dumpSendPacketDownstreamAvgInfoAsJson` snapshots rolling averages into metrics JSON. `collectThreadLocalStates` flushes thread-local rolling-average state.

`getOutliers` either returns test-injected outlier metrics or obtains aggregate latency stats requiring `minOutlierDetectionSamples` and passes them to `OutlierDetector.getOutlierMetrics`. Setters update both local volatile thresholds and detector thresholds. No state is persisted beyond metrics rolling windows.

## Dependencies, Integration, Risks, and Tests

Dependencies include `MutableRollingAverages`, `MetricsJsonBuilder`, `OutlierDetector`, `OutlierMetrics`, and DFS slow-peer config keys. It integrates with DataNode packet responder / write pipeline reporting.

Risks include caller-provided peer address formatting becoming metric names, thread-local state not being collected before outlier checks, stale test overrides, and threshold tuning producing false positives/negatives. Tests should cover minimum sample filtering, JSON dump format, outlier detection thresholds, setter validation, thread-local collection, and direct test outlier injection.
