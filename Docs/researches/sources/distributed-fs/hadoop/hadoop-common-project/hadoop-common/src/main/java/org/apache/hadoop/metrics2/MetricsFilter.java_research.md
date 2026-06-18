## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsFilter.java

Purpose: Abstract plugin contract for accepting or rejecting metrics sources, records, tags, and metric names.

Important APIs/types/functions: Extends `MetricsPlugin`; declares `accepts(String)`, `accepts(MetricsTag)`, and `accepts(Iterable<MetricsTag>)`. Provides a default record-level `accepts(MetricsRecord)` based on record name and tags.

Control flow: Metrics collection and sink adapters call filters before recording, JMX caching, or sink publication. Concrete filters compile configuration during `init`.

State and persistence: Base class has no state; concrete filters keep compiled patterns.

Dependencies/integration: Used in source, record, and metric filtering in `MetricsCollectorImpl`, `MetricsSourceAdapter`, `MetricsSinkAdapter`, and `MetricsConfig`.

Risks/test signals: Filter semantics combine name and tag acceptance; tests should cover whitelist-only, blacklist, and mixed tag/name scenarios.
