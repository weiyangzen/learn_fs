## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordFiltered.java

Purpose: Wrapper around a `MetricsRecord` that filters its metrics iterable for sink delivery.

Important APIs/types/functions: Delegates metadata, timestamp, context, and tags to the wrapped record; `metrics()` returns only metrics accepted by a `MetricsFilter`.

Control flow: `MetricsSinkAdapter.consume` wraps records when a metric filter is configured for a sink.

State and persistence: Holds wrapped record and filter references; no mutation.

Dependencies/integration: Uses Guava-style filtering/iterables or equivalent to lazily filter metrics.

Risks/test signals: Lazy filtering must remain stable while iterated by sinks. Tests should ensure tags are not filtered and metric-name predicates are applied.
