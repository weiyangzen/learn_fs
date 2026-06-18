<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AMultipartUploaderStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AMultipartUploaderStatistics.java

Purpose: statistics contract for the S3A multipart uploader API.

Important APIs/types/functions: extends `Closeable` and `DurationTrackerFactory`. Methods record instantiated uploader, upload started, part put with byte length, upload completed, upload aborted, and abort-uploads-under-path invocation.

Control flow: multipart uploader implementation calls these methods around upload lifecycle and cleanup actions.

State/persistence: interface only.

Dependencies/integration: created by `S3AStatisticsContext.createMultipartUploaderStatistics()` and implemented by `S3AMultipartUploaderStatisticsImpl`.

Risks/test signals: incorrect part byte accounting skews throughput/cost metrics. Tests should assert each multipart lifecycle method maps to the right `Statistic`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AMultipartUploaderStatistics.java -->
