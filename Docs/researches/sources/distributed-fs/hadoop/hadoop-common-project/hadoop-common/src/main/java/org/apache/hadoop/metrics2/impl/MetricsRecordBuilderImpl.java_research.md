## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordBuilderImpl.java

Purpose: Concrete record builder that applies filters and creates immutable metric objects.

Important APIs/types/functions: Stores parent collector, timestamp, record info, metric/tag lists, filters, and acceptable flag. Implements all builder methods and `getRecord`.

Control flow: Record-level name filtering sets `acceptable` at construction. Metric methods check metric filter before creating `MetricCounter*` or `MetricGauge*`. `getRecord` also applies tag-based record filtering before returning `MetricsRecordImpl`.

State and persistence: Mutable lists during building; returns unmodifiable views to the record constructor. Timestamp captured at construction.

Dependencies/integration: Used by `MetricsCollectorImpl`, mutable metrics, and annotations-generated sources.

Risks/test signals: `add(MetricsTag)` and `add(AbstractMetric)` bypass filter checks, so callers must use proper paths where filtering is expected. Tests should cover timestamping, context tag, metric filters, and unmodifiable records.
