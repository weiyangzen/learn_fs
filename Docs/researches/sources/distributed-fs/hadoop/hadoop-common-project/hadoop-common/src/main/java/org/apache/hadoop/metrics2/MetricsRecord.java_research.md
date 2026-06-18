## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsRecord.java

Purpose: Public immutable snapshot view of one metrics record.

Important APIs/types/functions: Exposes `timestamp`, `name`, `context`, `tags`, and `metrics`.

Control flow: Implementations derive context from a `Context` tag and provide iterable tags/metrics to sinks, filters, and JMX adapters.

State and persistence: Interface only. `MetricsRecordImpl` stores timestamp plus immutable tag/metric lists.

Dependencies/integration: Produced by `MetricsRecordBuilderImpl`, wrapped by `MetricsRecordFiltered`, iterated by `MetricsSinkAdapter`, and exposed to `MetricsSink.putMetrics`.

Risks/test signals: Tags and metrics should be immutable from callers' perspective. Tests should assert context fallback and filtering behavior.
