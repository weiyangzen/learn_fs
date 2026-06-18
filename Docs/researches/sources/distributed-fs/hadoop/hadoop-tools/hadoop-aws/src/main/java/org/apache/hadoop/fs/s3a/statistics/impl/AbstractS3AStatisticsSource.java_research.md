<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AbstractS3AStatisticsSource.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AbstractS3AStatisticsSource.java

Purpose: base class for S3A statistics implementations backed by an `IOStatisticsStore`.

Important APIs/types/functions: `getIOStatistics()` returns the store; protected `setIOStatistics()` binds it; `incCounter()`, `incCounter(name,value)`, `incGauge()`, `lookupCounterValue()`, `lookupGaugeValue()`, and `trackDuration()` delegate to the store.

Control flow: subclasses construct/configure an `IOStatisticsStore`, call `setIOStatistics()`, then use helper methods to update metrics.

State/persistence: stores one mutable in-memory `IOStatisticsStore` reference. No external persistence.

Dependencies/integration: Hadoop `IOStatisticsStore`, `IOStatisticsSource`, and `DurationTrackerFactory`.

Risks/test signals: `setIOStatistics()` must be called before helpers are used. Tests should cover null/uninitialized misuse in subclasses, counter/gauge lookups, duration tracker creation, and `toString()` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AbstractS3AStatisticsSource.java -->
