<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticsContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticsContext.java

Purpose: factory and aggregate sink for S3A component-specific statistics.

Important APIs/types/functions: extends `CountersAndGauges`. Factory methods create input stream, committer, block output stream, delegation token, AWS SDK, and multipart uploader statistics objects.

Control flow: filesystem/store setup provides a context; components ask it for specialized statistics instances and also use it directly for aggregate counter/gauge/duration events.

State/persistence: interface only. Implementations may bind to live filesystem instrumentation or no-op contexts.

Dependencies/integration: implemented by `BondedS3AStatisticsContext` and `EmptyS3AStatisticsContext`.

Risks/test signals: wrong context binding can drop or double-count metrics. Tests should verify new instances are wired to filesystem instrumentation and empty context returns safe no-op instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticsContext.java -->
