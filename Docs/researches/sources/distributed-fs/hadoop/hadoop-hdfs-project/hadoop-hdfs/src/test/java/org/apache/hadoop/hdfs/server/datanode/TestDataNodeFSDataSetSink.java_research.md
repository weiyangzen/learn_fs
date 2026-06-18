# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeFSDataSetSink.java

## Purpose

`TestDataNodeFSDataSetSink` verifies that a `SimulatedFSDataset` registered as a Hadoop Metrics2 source emits the expected FS dataset metrics and tags to a registered sink. The test is a metrics publication smoke test for DataNode dataset capacity, cache, failure, context, and host fields rather than a filesystem data-path test.

## Important APIs, Types, and Functions

The file defines one nested sink, `FSDataSetSinkTest`, implementing `MetricsSink`. Its `init` method seeds a `TreeSet` of expected names: `DfsUsed`, `Capacity`, `Remaining`, `StorageInfo`, failed-volume fields, cache fields, `Context`, and `Hostname`. `putMetrics` scans `MetricsRecord.metrics()` and `MetricsRecord.tags()` once, incrementing `count` for each expected metric or tag found. `testFSDataSetMetrics` constructs `HdfsConfiguration`, `SimulatedFSDataset`, `MetricsSystemImpl`, registers source and sink, publishes immediately, and asserts that all expected keys were observed.

## Control Flow

The test creates a simulated dataset, adds a block pool, initializes and starts a dedicated `MetricsSystemImpl`, registers the dataset as `FSDataSetSource`, registers the custom sink as `FSDataSetSink`, starts MBeans, and calls `publishMetricsNow`. It then sleeps four seconds to allow asynchronous delivery before shutting down Metrics2 state and comparing expected-key count with discovered-key count.

## State and Persistence Behavior

All state is in memory: static metrics system instance, simulated dataset, sink key set, and callback count. There is no disk-backed HDFS cluster and no block persistence. The test does exercise process-global metrics registration and MBean startup/shutdown, so cleanup order matters to avoid leaking metrics state between tests.

## Dependencies and Integration Points

The test integrates Hadoop Metrics2 (`MetricsSystemImpl`, `MetricsSink`, `MetricsRecord`, `MetricsTag`), HDFS configuration, and `SimulatedFSDataset` as the dataset metrics source. It checks the DataNode FS dataset metrics surface that external sinks and JMX consumers rely on.

## Risks and Edge Cases

The sink only counts the first metrics record (`count == 0`), so later records cannot repair a partial first callback. The fixed `Thread.sleep(4000)` is timing-sensitive. Because `MetricsSystemImpl` is static, missed shutdown or duplicate names could cause cross-test interference. The assertion is sensitive to metric/tag renames or removals but does not validate metric values.

## Test Signals

Primary signal is `assertEquals(sink.getMapCount(), sink.getFoundKeyCount())`. Failures indicate a missing expected metrics/tag name, callback delivery failure, or Metrics2 registration problem. There is no negative-path or value-level coverage.
