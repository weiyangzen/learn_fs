## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricCounterInt.java

Purpose: Immutable integer counter metric implementation.

Important APIs/types/functions: Constructor stores `MetricsInfo` and int value; `value()` returns `Integer`; `type()` returns `COUNTER`; `visit` calls `MetricsVisitor.counter(info,value)`.

Control flow: Created by `MetricsRecordBuilderImpl.addCounter` and consumed by records, sinks, JMX, and visitors.

State and persistence: Final primitive value and inherited metadata; no mutation.

Dependencies/integration: Extends `AbstractMetric` and implements counter visitor dispatch.

Risks/test signals: Tests should verify type, boxed value, visitor overload, equality, and toString inherited behavior.
