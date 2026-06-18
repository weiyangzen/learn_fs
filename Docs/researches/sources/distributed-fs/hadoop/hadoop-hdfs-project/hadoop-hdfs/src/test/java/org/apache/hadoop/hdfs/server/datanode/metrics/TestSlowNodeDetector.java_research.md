# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/metrics/TestSlowNodeDetector.java

## Purpose

`TestSlowNodeDetector` is the direct unit test for `OutlierDetector`. It validates median and median absolute deviation calculations and the slow-node selection rules that combine minimum peer count, low-latency threshold, median multiplier, and MAD-based statistical outliers.

## Important APIs and types

- `OutlierDetector.getOutliers(Map<String, Double>)` returns high-latency outlier nodes.
- Static helpers `computeMedian` and `computeMad` are tested against a matrix of generated numeric lists.
- `LOW_THRESHOLD` is 1000 and `MIN_OUTLIER_DETECTION_PEERS` is 3.
- Guava immutable collections and Apache `Pair` encode expected matrices.

## Control flow

Setup constructs an `OutlierDetector` and enables trace logging. The outlier matrix covers too few peers, statistical outliers below the low threshold, outliers above the low threshold, values inside and outside the median-multiplier limit, multi-node sets with high and low outliers, and cases where only high outliers should be returned.

Median and MAD tests sort a copy of each input list before invoking the static helpers, compare against expected values using a 0.001 percent error tolerance, and special-case one-element MAD near zero. Empty-list tests assert `IllegalArgumentException`, though the MAD test currently calls `computeMedian` in its lambda, which still validates empty-list rejection but not the intended method.

## State and persistence behavior

All state is in-memory immutable test data. There is no metrics scheduler or DataNode. The detector instance is recreated before each test.

## Dependencies and integration points

The file is the statistical core companion to `DataNodePeerMetrics` tests. It defines the expected behavior used to flag slow packet-sending peers and shapes the semantics of `OutlierMetrics` production.

## Risks and edge cases

- Expected floating-point values are hard-coded; algorithm changes require careful recalculation.
- The empty MAD test appears to invoke `computeMedian`, leaving direct empty-list `computeMad` behavior less explicitly covered.
- Input lists are sorted by the tests before median/MAD calls, so unsorted input handling is not asserted here.
- Low outliers are intentionally ignored because the detector targets slow nodes only.

## Test signals

Strong signals are matrix-driven outlier expectations, threshold and median-multiplier coverage, median/MAD numeric accuracy across list sizes one through ten, and explicit empty-input exception checks.
