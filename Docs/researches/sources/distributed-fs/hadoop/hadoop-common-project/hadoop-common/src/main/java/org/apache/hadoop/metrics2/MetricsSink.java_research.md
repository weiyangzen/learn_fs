## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSink.java

Purpose: Public plugin contract for receiving metrics records.

Important APIs/types/functions: Extends `MetricsPlugin`; declares `putMetrics(MetricsRecord record)` and `flush()`.

Control flow: `MetricsSinkAdapter` filters buffered records, calls `putMetrics` for each accepted record, then flushes once per consumed buffer.

State and persistence: Interface only; concrete sinks may persist to files, network services, or in-memory stores.

Dependencies/integration: Registered with `MetricsSystem`; can be configured reflectively from metrics properties.

Risks/test signals: Slow or throwing sinks interact with queue backpressure and retry logic. Tests should simulate put/flush failures, closeable sinks, and context/filter matching.
