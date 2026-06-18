## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsCollector.java

Purpose: Public collection interface used by `MetricsSource` implementations to start one or more records during a snapshot.

Important APIs/types/functions: `addRecord(String)` and `addRecord(MetricsInfo)` return `MetricsRecordBuilder` instances.

Control flow: Implementations decide whether a record is accepted by filters before returning the builder. Sources call this from `getMetrics`.

State and persistence: Interface only; implementation state lives in `MetricsCollectorImpl`.

Dependencies/integration: The central handoff from source code to metrics records. `MetricsSystemImpl` reuses one collector during sampling and clears it between sources.

Risks/test signals: Builder parent/end-record chaining depends on this contract. Tests should ensure source implementations can add multiple records and filtered records are omitted.
