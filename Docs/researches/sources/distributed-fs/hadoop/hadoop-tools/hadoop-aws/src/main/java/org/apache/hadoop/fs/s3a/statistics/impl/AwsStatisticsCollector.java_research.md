<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AwsStatisticsCollector.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AwsStatisticsCollector.java

Purpose: AWS SDK v2 `MetricPublisher` that translates SDK metric collections into S3A statistics callbacks.

Important APIs/types/functions: constructor accepts `StatisticsFromAwsSdk`. `publish(MetricCollection)` recursively flattens child metric collections, maps `CoreMetric.RETRY_COUNT` to retry and request counts, counts HTTP 429 throttles, and forwards durations for API call, service call, marshalling, signing, and unmarshalling. Helper methods `timing()`, `counter()`, and `recurseThroughChildren()` keep extraction generic. `close()` is no-op.

Control flow: AWS SDK calls `publish()` after API calls. The collector walks nested metrics because SDK metrics are stored at API call, attempt, and HTTP client levels.

State/persistence: holds final destination collector only; throttling count is local per publish call.

Dependencies/integration: AWS `MetricCollection`, `SdkMetric`, `CoreMetric`, `HttpMetric`, `HttpStatusCode`, and `StatisticsFromAwsSdk`.

Risks/test signals: request count is inferred as retries plus one when retry metric appears; missing retry metric could undercount requests. Tests should build nested metric collections with multiple attempts, throttles, and durations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/statistics/impl/AwsStatisticsCollector.java -->
