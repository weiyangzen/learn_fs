## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsBuffer.java

Purpose: Immutable-ish container grouping sampled records by source name for sink publication.

Important APIs/types/functions: Contains iterable `Entry` objects where each entry has a source name and iterable records. Copy constructor is used by waitable immediate buffers.

Control flow: `MetricsBufferBuilder` creates buffers during sampling; `MetricsSinkAdapter` iterates entries and records for filtering and sink calls.

State and persistence: Holds lists of entries/records in memory for one publication cycle.

Dependencies/integration: Links `MetricsSystemImpl.sampleMetrics` to asynchronous sink queues.

Risks/test signals: Buffer copy semantics matter for immediate publish. Tests should assert iteration order and stable records after builder completion.
