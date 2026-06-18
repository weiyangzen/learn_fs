## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MsInfo.java

Purpose: Built-in `MetricsInfo` enum for common metrics-system tags and counters.

Important APIs/types/functions: Enum constants cover context, hostname, active/all source and sink counts, and likely other system metadata. `description()` returns the stored description; `toString()` returns name/description style metadata.

Control flow: No dynamic control flow beyond enum use.

State and persistence: Enum constants with descriptions.

Dependencies/integration: Used by registries, record builders, and `MetricsSystemImpl.getMetrics`.

Risks/test signals: Renaming constants changes emitted metric/tag names. Tests should assert public system metric names and descriptions.
