<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/BondedS3AStatisticsContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/BondedS3AStatisticsContext.java

Purpose: real `S3AStatisticsContext` bonded to filesystem instrumentation and per-filesystem instance statistics.

Important APIs/types/functions: constructor accepts `S3AFSStatisticsSource`, which supplies `S3AInstrumentation` and `FileSystem.Statistics`. Factory methods create instrumentation-backed input stream, committer, block output, delegation token, AWS SDK, and multipart uploader statistics. Counter/gauge/quantile/duration methods forward to instrumentation. `trackDuration()` delegates to the instrumentation duration tracker.

Control flow: the filesystem creates this context and hands it to S3A components. Components create specialized stats objects or record aggregate events, all routed into shared instrumentation.

State/persistence: holds the statistics source reference; actual mutable metric state resides in `S3AInstrumentation` and filesystem statistics.

Dependencies/integration: depends on `S3AInstrumentation`, `FileSystem.Statistics`, `Statistic`, and implementation classes such as `StatisticsFromAwsSdkImpl` and `S3AMultipartUploaderStatisticsImpl`.

Risks/test signals: source methods must return live instrumentation. Tests should verify each factory binds counters to the same source, counter/gauge deltas reach instrumentation, and durations close correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/BondedS3AStatisticsContext.java -->
