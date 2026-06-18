## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableCounter.java

Purpose: Abstract base for mutable monotonically increasing counter metrics.

Important APIs/types/functions: Extends `MutableMetric` and defines counter semantics for concrete int/long counters.

Control flow: Concrete counters increment internal values and snapshot as counters.

State and persistence: Base class contributes changed-state tracking via `MutableMetric`; concrete classes store numeric values.

Dependencies/integration: Parent of `MutableCounterInt` and `MutableCounterLong`, used by registry and annotations.

Risks/test signals: Counters should not expose decrement paths. Tests should cover changed flag interaction with snapshot `all=false`.
