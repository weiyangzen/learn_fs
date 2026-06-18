## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricGaugeLong.java

Purpose: Immutable long gauge metric implementation.

Important APIs/types/functions: Stores long value, returns `Long`, reports `GAUGE`, and dispatches to `MetricsVisitor.gauge(info,long)`.

Control flow: Built by record builders for long-valued instantaneous readings.

State and persistence: Final value and metadata only.

Dependencies/integration: Supports `MutableGaugeLong` and long gauge builder overloads.

Risks/test signals: Large value and visitor-overload tests protect against int truncation.
