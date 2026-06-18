# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithHdfs.java

## Purpose
This class tests `RollingFileSystemSink` against a live non-secure HDFS MiniDFSCluster, covering writes, append/overwrite behavior, error handling when HDFS disappears, flush-thread behavior, and initialization when HDFS is unavailable.

## Important APIs, types, and functions
- `setupHdfs()` starts a four-DataNode cluster and clears `RollingFileSystemSink.hasFlushed`.
- Tests use inherited helpers from `RollingFileSystemSinkTestBase`: `initMetricsSystem`, `doWriteTest`, `doAppendTest`, `assertMetricsContents`, `assertExtraContents`, `findMostRecentLogFile`, and `getLogFilename`.
- `MockSink.errored` and `MockSink.initialized` capture expected sink error behavior.

## Control flow
Basic write/append tests build an `hdfs://namenode/tmp` path, initialize a metrics system, publish metrics through inherited helpers, and assert file contents. Failure tests initialize the sink, optionally publish once, shut down HDFS, then publish or stop the metrics system and assert whether errors are reported according to ignore-errors mode. `testFlushThread` forces the sink flusher thread, publishes twice, waits up to 10 seconds for `hasFlushed`, then checks the current log file length in HDFS.

## State and persistence behavior
Each test gets a fresh MiniDFSCluster and writes metrics files under `/tmp` in HDFS. The metrics system maintains sink state and background flushing. Static test flags on `RollingFileSystemSink` and `MockSink` are mutated and reset where needed. Cluster shutdown is per test.

## Dependencies and integration points
The test integrates Hadoop metrics2 `MetricsSystem`, `RollingFileSystemSink`, HDFS append semantics, MiniDFSCluster availability, HDFS `FileSystem` path resolution, and time-bucketed rolling log paths based on `DATE_FORMAT`.

## Risks and edge cases
Flush-thread validation is timing-sensitive and uses polling. The tests assume four DataNodes are enough for append semantics and replication. Error-path assertions depend on shutdown timing and whether sink operations surface exceptions synchronously or through `MockSink.errored`.

## Test signals
Passing confirms rolling metrics can write to HDFS, append or create new files according to append settings, honor silent error mode, survive missing HDFS during init when configured to ignore errors, and flush buffered metrics to HDFS via the background thread.
