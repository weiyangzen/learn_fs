# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInstrumentation.java

## Purpose
`S3AInstrumentation` is the central metrics and IOStatistics implementation for an `S3AFileSystem` instance. It registers the filesystem with Hadoop Metrics2, declares every `Statistic` counter/gauge/duration, exposes `IOStatisticsSource`, and creates per-stream/per-committer/per-token statistics adapters.

## Important APIs, Types, and Functions
Key APIs are `getIOStatistics()`, `getDurationTrackerFactory()`, `trackDuration()`, `createMetricsUpdatingStore()`, `newInputStreamStatistics()`, `newOutputStreamStatistics()`, `newCommitterStatistics()`, `newDelegationTokenStatistics()`, `incrementCounter()`, `incrementGauge()`, `recordDuration()`, `dump()`, `toMap()`, and `close()`. Internal types include `MetricUpdatingDurationTracker`, `MetricDurationTrackerFactory`, `InputStreamStatistics`, `OutputStreamStatistics`, `CommitterStatisticsImpl`, `DelegationTokenStatisticsImpl`, `MetricsToMap`, and `MetricsUpdatingIOStatisticsStore`.

## Control Flow and State
Construction tags the registry with filesystem id and bucket, creates counters/gauges/duration counters from the `Statistic` enum, registers a weak Metrics2 source, builds the instance `IOStatisticsStore`, then pairs IOStatistics duration tracking with Metrics2 counter updates. Stream statistics collect local atomic counters during reads/writes and merge them into filesystem-wide metrics on `close()`, `unbuffered()`, or stream leak handling. Output statistics track block upload queue/active gauges and merge upload counters on close. `close()` unregisters the metrics source, stops quantiles, decrements the active source count, and shuts down the shared metrics system when the last source closes.

## State and Persistence Behavior
State is in-memory only: a static metrics system and source counters, one Metrics2 registry per filesystem, a filesystem-level `IOStatisticsStore`, and per-stream stores. Atomic counters support cross-thread stream activity, but merge points are explicit and some filesystem thread-local `FileSystem.Statistics` updates happen only during close. Quantiles start background work and must be stopped.

## Dependencies and Integration Points
The class integrates with Hadoop Metrics2, `WeakRefMetricsSource`, `IOStatisticsBinding`, `Statistic`, `StoreStatisticNames`, `StreamStatisticNames`, `S3AInputStreamStatistics`, `BlockOutputStreamStatistics`, committer statistics, delegation token statistics, and filesystem `FileSystem.Statistics`. It is consumed by S3A filesystem/store/read/write code to report object, stream, audit, committer, throttle, and duration metrics.

## Risks and Test Signals
Risks include stale metrics if streams are not closed/merged, gauge imbalance on failed uploads/prefetches, static metrics-system lifecycle races, quantile scheduler leakage if `close()` is skipped, and incomplete synchronization between Metrics2 counters and IOStatistics for specialized stores. Tests should verify metrics source registration/unregistration, counter/gauge increments, duration success/failure counters, input stream merge on close/unbuffer/leak, output stream gauge cleanup, committer counter updates, and storage statistics visibility.
