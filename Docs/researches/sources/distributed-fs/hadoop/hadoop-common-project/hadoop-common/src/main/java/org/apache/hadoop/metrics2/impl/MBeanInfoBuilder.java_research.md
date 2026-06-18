## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MBeanInfoBuilder.java

Purpose: Builds JMX `MBeanInfo` metadata from the latest metrics records for a source.

Important APIs/types/functions: Constructor accepts name and description; `reset(Iterable<MetricsRecordImpl>)` rebuilds attributes; `get()` returns `MBeanInfo`.

Control flow: `MetricsSourceAdapter.updateInfoCache` resets the builder using sampled records after refreshing the attribute cache. Tags and metrics become JMX attributes with names matching adapter tag/metric naming rules.

State and persistence: Mutable builder state for current attribute descriptors; cached in `MetricsSourceAdapter`.

Dependencies/integration: Uses JMX metadata types and Hadoop metrics records.

Risks/test signals: Multi-record attribute suffixing must align with `MetricsSourceAdapter` attr cache. Tests should cover tag attributes, metric attributes, duplicate names, and cache refresh.
