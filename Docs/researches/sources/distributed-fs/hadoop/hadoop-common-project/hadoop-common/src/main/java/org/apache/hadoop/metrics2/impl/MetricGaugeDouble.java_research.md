## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeDouble.java

Purpose: Immutable double gauge metric implementation.

Important APIs/types/functions: Stores double value, returns `Double`, reports `MetricType.GAUGE`, and visits the double gauge overload.

Control flow: Created by builders for floating-point gauges such as averages and standard deviation.

State and persistence: Final value and inherited metadata only.

Dependencies/integration: Used by mutable stats and rolling-average metrics.

Risks/test signals: Tests should cover NaN/infinity behavior if upstream stats can produce them, plus visitor dispatch.
