<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/CountersAndGauges.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/CountersAndGauges.java

Purpose: shared statistics sink for S3A counters, gauges, quantiles, and durations.

Important APIs/types/functions: extends `DurationTrackerFactory`. Methods increment counters/gauges, decrement gauges, add quantile values, and record completed durations with success status.

Control flow: components receive a context implementing this interface and emit numeric events by `Statistic` enum key.

State/persistence: interface only. Implementations may forward into `S3AInstrumentation` and `IOStatisticsStore`.

Dependencies/integration: base for `S3AStatisticsContext` and `S3AStatisticInterface` behavior.

Risks/test signals: invalid statistic keys or incorrect sign on gauges can corrupt metrics. Tests should cover counter/gauge increments, duration success/failure paths, and quantile recording.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/CountersAndGauges.java -->
