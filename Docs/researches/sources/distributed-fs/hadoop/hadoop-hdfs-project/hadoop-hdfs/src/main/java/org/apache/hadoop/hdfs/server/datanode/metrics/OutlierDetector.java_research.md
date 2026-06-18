# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/OutlierDetector.java

## Purpose

`OutlierDetector` is a reusable latency outlier detector for DataNode resources such as disks and peer nodes. It applies median absolute deviation with conservative low-threshold and median-multiplier safeguards.

## Important APIs, Control Flow, and State

`getOutliers` returns a simple resource-to-latency map, while `getOutlierMetrics` returns `OutlierMetrics` containing median, MAD, computed upper limit, and actual latency. The detector skips analysis when the resource count is below `minNumResources`. Otherwise it sorts latency values, computes median, computes MAD as median absolute deviation multiplied by `1.4826`, and sets the outlier limit to the maximum of `lowThresholdMs`, `median * 3`, and `median + 3 * mad`. Entries above that limit are flagged.

State consists of volatile `minNumResources` and `lowThresholdMs`, updated by setters. Static helpers `computeMedian` and `computeMad` require non-empty sorted input and throw `IllegalArgumentException` otherwise. There is no persistence.

## Dependencies, Integration, Risks, and Tests

Dependencies include `OutlierMetrics`, Guava `ImmutableMap`, and SLF4J. It is used by `DataNodeDiskMetrics` and `DataNodePeerMetrics`.

Risks include handling NaN/Infinity latencies, requiring callers to provide comparable aggregate metrics, sorting overhead for large maps, and threshold choices that can mask uniformly bad resources. Tests should cover odd/even median, MAD computation, insufficient sample count, low-threshold floor, median-multiplier floor, exact boundary comparisons, and returned `OutlierMetrics` values.
