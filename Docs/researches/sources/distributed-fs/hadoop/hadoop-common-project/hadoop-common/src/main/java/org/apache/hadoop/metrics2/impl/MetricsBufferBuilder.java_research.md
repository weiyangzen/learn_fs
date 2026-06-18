## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsBufferBuilder.java

Purpose: Simple builder for collecting source-name to metrics-record entries before publishing.

Important APIs/types/functions: `add(String, Iterable<MetricsRecordImpl>)` appends entries and `get()` returns a `MetricsBuffer`.

Control flow: `MetricsSystemImpl.sampleMetrics` calls `add` once per accepted source, then calls `get`.

State and persistence: Mutable in-memory list for the current snapshot only.

Dependencies/integration: Consumes records from `MetricsSourceAdapter.getMetrics`.

Risks/test signals: Tests should cover empty sources, multiple sources, and preservation of source order.
