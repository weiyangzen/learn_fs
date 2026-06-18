## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeInt.java

Purpose: Immutable integer gauge metric implementation.

Important APIs/types/functions: Stores int value, returns `Integer`, reports `GAUGE`, and visits the int gauge overload.

Control flow: Produced by `MetricsRecordBuilderImpl.addGauge(MetricsInfo,int)`.

State and persistence: Final primitive and metadata.

Dependencies/integration: Used for queue sizes, active source counts, and mutable int gauges.

Risks/test signals: Tests should ensure it is not reported as counter and that visitor dispatch uses the gauge path.
