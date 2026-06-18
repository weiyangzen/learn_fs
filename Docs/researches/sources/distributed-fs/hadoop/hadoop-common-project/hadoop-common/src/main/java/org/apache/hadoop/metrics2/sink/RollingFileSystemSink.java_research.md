<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSink.java

## Purpose
`RollingFileSystemSink` writes metrics2 records to a Hadoop `FileSystem`, typically HDFS, rolling output into GMT timestamped directories. It is intended for cluster-wide metrics logs where each process writes `source-host.log` files under a configured base path.

## Important APIs and Types
It implements `MetricsSink` and `Closeable`. Configuration keys include `basepath`, `source`, `ignore-error`, `allow-append`, `roll-interval`, `roll-offset-interval-millis`, `keytab-key`, and `principal-key`. Visible-for-testing hooks include supplied configuration/filesystem, roll timings, and flush flags.

## Control Flow
`init` records configuration, parses roll intervals, loads a Hadoop `Configuration`, configures UGI, and performs Kerberos login when security is enabled. Filesystem initialization is delayed until the first write. `rollLogDirIfNeeded` creates the base directory, validates append support, calculates the current GMT interval directory, closes an old stream, opens a new file, updates the next flush time, and schedules a timer task to close the prior stream. `putMetrics` serializes one line per record and calls `hflush` to make interval data durable.

## State and Persistence
Persistent state is the file data written to the configured filesystem. In-memory state tracks the active filesystem, directory, file path, print stream, FS stream, timer, and roll schedule. The sink serializes write/roll/close operations with a private lock.

## Dependencies and Integration Points
It integrates metrics2, Hadoop `FileSystem`, UGI/Kerberos, `SecurityUtil`, `Path`, and HDFS append semantics. External readers consume interval directories named `yyyyMMddHHmm`.

## Risks and Test Signals
Risks include filesystem-specific append behavior, expensive hflush calls, timer races with writes, suffix probing in large directories, incorrect `file.startsWith(base)` comparisons against file names, and misleading Javadoc around `ignore-error` defaults. Tests should cover roll interval parsing, non-negative offsets, secure login validation, append fallback, suffix selection, timer close behavior, first-write initialization failure, hflush errors, and concurrent `putMetrics`/`close` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSink.java -->
