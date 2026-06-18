# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestPrometheusMetricsSink.java

## Purpose
Tests `PrometheusMetricsSink` publishing, deduplication by metric plus tags, flush freshness, Prometheus name normalization, and special TopMetrics label parsing.

## Important APIs, Types, And Functions
Uses `PrometheusMetricsSink.writeMetrics()`, `prometheusName()`, `DefaultMetricsSystem`, annotated `TestMetrics`, and a custom `TestTopMetrics implements MetricsSource`. Assertions check emitted text and normalized names.

## Control Flow
Publishing tests initialize the default metrics system, register the sink and sources, mutate counters, publish metrics, write sink output to a UTF-8 stream, and inspect the resulting exposition text. Dedup tests register two sources with different tag values. Flush tests unregister and re-register with different tags between publishes. Naming tests call `prometheusName()` directly.

## State And Persistence Behavior
Sink output is in-memory, but the sink maintains the most recent flushed metrics set. Tests stop and shut down the default metrics system after use; missing cleanup would cross-contaminate global metrics state.

## Dependencies And Integration Points
Integrates metrics2 source collection with Prometheus exposition formatting, Hadoop metric/tag naming conventions, `StringUtils.deleteWhitespace`, and NameNode TopMetrics-style record/metric names encoded with dot-separated label fragments.

## Risks
The global `DefaultMetricsSystem` is shared, so cleanup is essential. Deduplication must include labels/tags, not just metric name. Name normalization must handle camel case, periods, whitespace, hyphens, UUID-like strings, and embedded label syntax.

## Test Signals
Expected signals include `test_metrics_num_bucket_create_fails{context="dfs",testtag="testTagValueN"`, absence of stale tag values after flush, normalized snake_case names, and TopMetrics labels such as `op="rename"` and `user="hadoop/TEST_HOSTNAME.com@HOSTNAME.COM"`.
