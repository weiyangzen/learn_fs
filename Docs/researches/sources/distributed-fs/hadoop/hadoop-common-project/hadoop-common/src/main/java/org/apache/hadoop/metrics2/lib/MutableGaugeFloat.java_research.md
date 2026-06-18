## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGaugeFloat.java

Purpose: Mutable float gauge.

Important APIs/types/functions: Constructor stores info and initial float; operations set/increment/decrement value; `value()` and `snapshot` expose it as a float gauge.

Control flow: Mutating operations set the changed flag; snapshot emits when all or changed.

State and persistence: In-memory float value.

Dependencies/integration: Created through `MetricsRegistry.newGauge` or field annotation.

Risks/test signals: Precision and NaN handling should be considered. Tests should cover set, incr, decr, snapshot, and changed clearing.
