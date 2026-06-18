# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodePeerMetrics.java

## Purpose

`TestDataNodePeerMetrics` verifies rolling-average peer latency metrics for downstream packet sending, including JSON reporting and stale record removal/reuse.

## Important APIs, Types, and Functions

The suite uses `DataNodePeerMetrics.create`, `MutableRollingAverages`, `MetricsTestHelper.replaceRollingAveragesScheduler`, `DFS_DATANODE_PEER_STATS_ENABLED_KEY`, and `DFS_DATANODE_PEER_METRICS_MIN_OUTLIER_DETECTION_SAMPLES_KEY`. Helper `genPeerAddress` creates randomized `[ip:9801]` peer strings.

## Control Flow

`testGetSendPacketDownstreamAvgInfo` enables peer stats, replaces the rolling average scheduler with two five-second windows, records 1000 random latencies for a new peer in each of three iterations, sleeps until after each rollover, dumps JSON through `dumpSendPacketDownstreamAvgInfoAsJson`, and checks the peer address appears. `testRemoveStaleRecord` configures a short validity period, records enough samples for three peers, waits for stats to appear, verifies JSON contains all peers, waits until stale records are removed and JSON becomes `{}`, then records the peers again and verifies metrics resume normally.

## State and Persistence Behavior

All metrics state is in memory in `MutableRollingAverages` and the peer metrics object. Records age out based on scheduler windows and validity milliseconds. There is no MiniDFSCluster or persisted filesystem state.

## Dependencies and Integration Points

The file integrates DataNode peer metrics, rolling-average scheduling, outlier-detection sample thresholds, metrics test helper scheduler replacement, and JSON dumping. It covers the peer-latency data source used by slow-peer detection/reporting.

## Risks and Edge Cases

The tests depend on real time and scheduler rollover, including computed sleeps. Random peer addresses prevent accidental key reuse but make logs nondeterministic. If rolling-average validity or JSON key naming changes, assertions may fail. The stale-record test verifies that eviction is not permanent by adding records again after JSON empties.

## Test Signals

Signals are JSON containing the active peer address after each rollover, rolling stats size becoming three, JSON becoming `{}` after stale eviction, and stats returning to three after re-adding samples.
