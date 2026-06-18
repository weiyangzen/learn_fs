## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricType.java

Purpose: Public enum identifying immutable metric semantics as `COUNTER` or `GAUGE`.

Important APIs/types/functions: The enum constants are consumed by `AbstractMetric.type()`, visitor logic, builders, and downstream sinks.

Control flow: No executable control flow beyond enum initialization.

State and persistence: Enum singletons only; no mutable state.

Dependencies/integration: Implemented by counter and gauge concrete metric classes and used by output adapters that need to distinguish monotonic counters from point-in-time gauges.

Risks/test signals: Adding enum constants would require visitor and sink changes. Existing tests should assert concrete metric classes return the expected type.
