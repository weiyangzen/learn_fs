<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/PutTrackerStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/PutTrackerStatistics.java

Purpose: statistics extension point for put tracker behavior.

Important APIs/types/functions: extends `S3AStatisticInterface`. In this source version it is a marker-style interface with no additional methods.

Control flow: output stream statistics can be passed where put tracker statistics are required.

State/persistence: interface only.

Dependencies/integration: inherited by `BlockOutputStreamStatistics`.

Risks/test signals: main risk is API drift if put tracker events are later added. Compile-time tests catch implementations that need updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/PutTrackerStatistics.java -->
