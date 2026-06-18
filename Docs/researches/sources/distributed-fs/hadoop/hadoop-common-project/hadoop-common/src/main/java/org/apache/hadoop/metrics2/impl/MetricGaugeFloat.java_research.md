## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeFloat.java

Purpose: Immutable float gauge metric implementation.

Important APIs/types/functions: Stores float value, returns `Float`, reports `GAUGE`, and calls `MetricsVisitor.gauge(info,float)`.

Control flow: Created by record builders and mutable float gauges.

State and persistence: Final value and metadata.

Dependencies/integration: Supports the public float gauge builder overload and `MutableGaugeFloat`.

Risks/test signals: Cover visitor overload and precision-preserving value boxing.
