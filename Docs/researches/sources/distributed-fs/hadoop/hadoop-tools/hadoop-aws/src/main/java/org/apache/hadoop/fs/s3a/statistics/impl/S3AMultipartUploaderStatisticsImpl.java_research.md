<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/S3AMultipartUploaderStatisticsImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/S3AMultipartUploaderStatisticsImpl.java

Purpose: real multipart uploader statistics implementation that maps uploader events to S3A `Statistic` counters and duration tracking.

Important APIs/types/functions: constructor accepts increment callback and duration tracker factory. Private `inc(Statistic,long)` forwards increments. Lifecycle methods increment instantiated, started, part byte/count, completed, aborted, and abort-under-path statistics. `trackDuration()` delegates to the duration tracker factory. `close()` is no-op.

Control flow: multipart uploader calls event methods; the implementation translates each event into one or more aggregate statistic updates.

State/persistence: holds callbacks only; metric state lives in the destination instrumentation.

Dependencies/integration: `Statistic`, `BiConsumer<Statistic,Long>`, and `DurationTrackerFactory`.

Risks/test signals: wrong statistic mapping affects user-visible counters. Tests should mock callbacks and verify exact statistics/counts for each event, especially part length bytes and count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/S3AMultipartUploaderStatisticsImpl.java -->
