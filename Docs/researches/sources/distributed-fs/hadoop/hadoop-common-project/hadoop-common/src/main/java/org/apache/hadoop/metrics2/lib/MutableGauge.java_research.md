## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableGauge.java

Purpose: Abstract base for mutable point-in-time gauge metrics.

Important APIs/types/functions: Extends `MutableMetric` and defines common gauge role for concrete numeric gauge types.

Control flow: Concrete gauges support set/increment/decrement and snapshot as gauges.

State and persistence: Base changed flag from `MutableMetric`; concrete classes store values.

Dependencies/integration: Parent of int, long, and float mutable gauges created by registry and annotations.

Risks/test signals: Gauge operations can go negative depending on caller; tests should cover changed tracking and snapshot type.
