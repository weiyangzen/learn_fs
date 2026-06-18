<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/BlockOutputStreamStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/BlockOutputStreamStatistics.java

Purpose: statistics contract for block-based S3A output streams.

Important APIs/types/functions: extends `Closeable`, `S3AStatisticInterface`, and `PutTrackerStatistics`. Methods record block queue/start/complete/failure events, bytes transferred/written, multipart complete/abort exceptions, pending upload bytes, committed uploaded size, allocated/released/active blocks, counter/gauge lookups, hflush/hsync calls, and conditional create outcomes.

Control flow: output stream code calls methods at block lifecycle and sync/write boundaries; implementations update IOStatistics, gauges, counters, and durations.

State/persistence: interface only. Implementations may hold counters/gauges in memory and publish into filesystem statistics.

Dependencies/integration: used by S3A block output streams, multipart put trackers, and IOStatistics consumers.

Risks/test signals: missing event calls skew active block/pending byte gauges. Tests should exercise successful upload, failed upload, conditional create, sync calls, and close semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/BlockOutputStreamStatistics.java -->
