<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/StatisticsFromAwsSdkImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/StatisticsFromAwsSdkImpl.java

Purpose: concrete AWS SDK statistics sink that records SDK counters and durations into a `CountersAndGauges` destination.

Important APIs/types/functions: constructor stores `CountersAndGauges`. Update methods increment request, retry, and throttle counters. Duration methods record request, client execute, marshalling, signing, and response processing durations as successful events. Static `mapErrorStatusCodeToStatisticName(int)` maps HTTP error status classes/specific statuses to S3A statistic names.

Control flow: `AwsStatisticsCollector` invokes this sink as metrics arrive from AWS SDK. This implementation translates events into `Statistic` keys.

State/persistence: holds destination reference only.

Dependencies/integration: depends on `CountersAndGauges`, `Statistic`, and Java `Duration`.

Risks/test signals: status-code mapping and duration statistic selection must match documented S3A metrics. Tests should cover request/retry/throttle increments, duration recording, and 4xx/5xx status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/StatisticsFromAwsSdkImpl.java -->
