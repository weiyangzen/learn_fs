<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticsFromAwsSdk.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticsFromAwsSdk.java

Purpose: sink interface for metrics emitted by AWS SDK v2 metric publishers.

Important APIs/types/functions: methods update AWS request count, retry count, throttle exception count, API/service request time, client execute time, request marshalling time, signing time, and response processing time.

Control flow: `AwsStatisticsCollector.publish()` maps nested AWS metric collections into these callbacks.

State/persistence: interface only.

Dependencies/integration: implemented by `StatisticsFromAwsSdkImpl`; produced by `S3AStatisticsContext.newStatisticsFromAwsSdk()`.

Risks/test signals: SDK metric naming changes can stop callbacks from firing. Tests should feed synthetic metric collections and verify request/retry/throttle/duration counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/StatisticsFromAwsSdk.java -->
