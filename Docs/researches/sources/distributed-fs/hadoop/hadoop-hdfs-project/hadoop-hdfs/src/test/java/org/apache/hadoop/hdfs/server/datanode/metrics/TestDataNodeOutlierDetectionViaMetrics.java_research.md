# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/metrics/TestDataNodeOutlierDetectionViaMetrics.java

## Purpose

`TestDataNodeOutlierDetectionViaMetrics` verifies that `DataNodePeerMetrics` detects slow downstream DataNode peers from rolling send-packet latency samples and returns no outliers when all peers are fast.

## Important APIs and types

- `DataNodePeerMetrics.addSendPacketDownstream` records per-peer latency samples.
- `dumpSendPacketDownstreamAvgInfoAsJson` triggers rolling-average snapshot publication.
- `getOutliers` returns a map from peer name to `OutlierMetrics`.
- `MetricsTestHelper.replaceRollingAveragesScheduler` shortens rolling-average windows for test runtime.
- Constants define 10 fast peers, one 20-second slow peer, and fast latencies below 5 ms.

## Control flow

Setup enables trace logging and creates an `HdfsConfiguration`. The outlier test constructs metrics, replaces the rolling scheduler with ten three-second windows, injects many samples for ten fast peers, injects many samples for one slow peer, dumps rolling averages, waits until outliers become non-empty, and asserts exactly the slow peer appears.

The no-outlier test uses the same scheduler and fast-peer injection, triggers a snapshot, and asserts the outlier map is empty. Helper methods add twice the configured minimum sample count per peer, ensuring both sample-count and minimum-peer thresholds are satisfied.

## State and persistence behavior

State is held in memory inside rolling-average metrics and the outlier cache. No cluster or filesystem is used. Random fast-node latencies make exact averages non-deterministic while staying far below the slow-node threshold.

## Dependencies and integration points

The test bridges Hadoop metrics rolling averages, DataNode peer latency recording, and the `OutlierDetector` statistical logic that produces `OutlierMetrics` for NameNode or operator reporting.

## Risks and edge cases

- Detection is asynchronous and uses a long wait timeout.
- Random fast latencies can make debugging harder, though the range is intentionally tiny.
- Only one extreme slow peer is tested; borderline outliers and changing latency over windows are not covered.
- The JSON dump is used as a trigger, but the JSON content itself is not parsed here.

## Test signals

Strong signals are minimum-peer coverage, minimum-sample coverage, scheduler replacement, explicit snapshot trigger, eventual detection of exactly one named outlier, and empty result under a fast-only population.
