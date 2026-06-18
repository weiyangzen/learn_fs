<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticInterface.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticInterface.java

Purpose: common base for S3A statistic sources that expose IOStatistics and duration tracking.

Important APIs/types/functions: extends `IOStatisticsSource` and `DurationTrackerFactory`.

Control flow: components can accept this interface when they only need statistics retrieval and duration tracker creation.

State/persistence: interface only.

Dependencies/integration: inherited by most S3A statistics contracts.

Risks/test signals: implementations should return non-null IOStatistics unless explicitly documented as an empty/no-op context. Compile-time use enforces duration tracker availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/S3AStatisticInterface.java -->
