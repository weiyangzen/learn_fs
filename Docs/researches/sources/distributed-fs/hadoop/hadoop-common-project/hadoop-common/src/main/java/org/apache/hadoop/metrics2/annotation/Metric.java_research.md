## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/Metric.java

Purpose: Runtime annotation for fields and methods that should become Hadoop metrics.

Important APIs/types/functions: `Type` enum includes `DEFAULT`, `COUNTER`, `GAUGE`, and `TAG`. Annotation attributes include `value`, `about`, `sampleName`, `valueName`, `always`, `type`, and `interval`.

Control flow: `MetricsSourceBuilder` scans fields and methods, and `MutableMetricsFactory` maps annotated members to mutable metrics or method-backed metrics.

State and persistence: Annotation metadata retained at runtime.

Dependencies/integration: Used with `@Metrics` on source classes and consumed by reflection utilities.

Risks/test signals: Unsupported field or method return types throw `MetricsException`. Tests should cover all annotation value-name combinations and quantile interval handling.
