<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/PrometheusMetricsSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/PrometheusMetricsSink.java

## Purpose
`PrometheusMetricsSink` is an in-memory metrics2 sink for Prometheus exporters. It captures the latest flushed set of gauge and counter metrics and writes them in Prometheus text exposition format on request.

## Important APIs and Types
The core methods are `putMetrics`, `flush`, `writeMetrics(Writer)`, `prometheusName`, and private TopMetrics helpers. It stores two concurrent maps, `nextPromMetrics` for the current metrics cycle and `promMetrics` for the last flushed snapshot. A bounded Guava `LoadingCache` memoizes Hadoop-to-Prometheus name normalization.

## Control Flow
`putMetrics` ignores metric types other than `COUNTER` and `GAUGE`, builds a normalized key from record name plus metric name, and stores the metric under the record's tag collection. `flush` atomically swaps the next map into the exported map and resets the next map. `writeMetrics` emits `HELP`, `TYPE`, and sample lines, with special parsing for NameNode TopMetrics so operation and user are exported as labels instead of embedded in metric names.

## State and Persistence
All state is process memory. A scrape sees only the most recently flushed metrics cycle. The name cache is static and capped at 100,000 entries.

## Dependencies and Integration Points
This sink feeds HTTP or servlet exporter code that calls `writeMetrics`. It depends on metrics2 record/tag contracts, Guava cache, Apache Commons `StringUtils`, and Prometheus naming conventions.

## Risks and Test Signals
Labels are not escaped, and a shared mutable `extendMetricsTags` list is cleared inside nested loops, so TopMetrics behavior needs careful coverage. Tests should verify normalization cache fallback, map swap semantics, filtering to counters/gauges, label omission of `numopenconnectionsperuser`, TopMetrics parsing, and empty-state output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/PrometheusMetricsSink.java -->
