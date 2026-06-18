# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSinkTestBase.java

## Purpose
Shared base for `RollingFileSystemSink` tests. It builds metrics-system configurations, creates sample metric sources, writes metrics to a filesystem target, reads rolled log files, validates output format, pre-creates existing log files, and wraps the sink to record errors.

## Important APIs, Types, And Functions
Key helpers are `initMetricsSystem()`, `doWriteTest()`, `readLogFile()`, `readLogData()`, `findMostRecentLogFile()`, `assertMetricsContents()`, `assertExtraContents()`, `doAppendTest()`, `preCreateLogFile()`, `getNowNotTopOfHour()`, and `assertFileCount()`. `MyMetrics1` and `MyMetrics2` are annotated sources. `MockSink` extends `RollingFileSystemSink` and tracks `errored`/`initialized`.

## Control Flow
Each test gets a method-specific directory. Configuration is written with a lowercase metrics prefix, sink class, base path, context filter, append/error flags, hourly roll interval, zero roll offset, and small queue. `doWriteTest()` registers sources, increments gauges, publishes once, stops and shuts down the metrics system, then reads the current or starting-hour directory. Append helpers create current-hour log files before the sink opens them.

## State And Persistence Behavior
Persistent state is local or configured Hadoop `FileSystem` content under `ROOT_TEST_DIR` and time-named directories. `DATE_FORMAT` is GMT and static. `methodDir` is static per current test method. `MockSink` flags are static volatile and must be reset by tests before checking error paths.

## Dependencies And Integration Points
Integrates with `MetricsSystemImpl`, `ConfigBuilder`, `TestMetricsConfig`, Hadoop `FileSystem`, `Path`, host name lookup for log file names, metrics annotations, and JUnit lifecycle extensions.

## Risks
Top-of-hour rollovers can make tests read the wrong directory, so `getNowNotTopOfHour()` avoids the last 20 seconds of an hour. Hostname-dependent log names and filesystem append semantics vary by environment. Regex assertions deliberately allow arbitrary tag/metric order but still require record order.

## Test Signals
Signals include exactly expected log file counts, correctly formatted metric records for both sources, preservation of pre-existing `"Extra stuff"` when append is allowed, and `MockSink.errored` reflecting whether errors are propagated or ignored.
