## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricStringBuilder.java

Purpose: `MetricsRecordBuilder` implementation that renders tags and metrics into a delimited string for diagnostics and textual dumps.

Important APIs/types/functions: Constructors configure prefix, suffix, separator, and key/value separator. `add(MetricsInfo,Object)` and `tuple(String,String)` append formatted entries. Overrides all tag, counter, and gauge builder methods plus `toString`.

Control flow: Each builder callback delegates to `add` or `tuple`; `setContext` writes a context tuple; `parent()` returns the configured collector. Separators are inserted only after the first entry.

State and persistence: Maintains a `StringBuilder`, formatting strings, and a parent collector reference. It is mutable, not synchronized, and intended for one build pass.

Dependencies/integration: Consumes `MetricsTag` and `AbstractMetric` from records and can be used wherever a `MetricsRecordBuilder` is accepted.

Risks/test signals: Formatting regressions affect human-readable output and tests should cover empty output, custom separators, tag/metric order, and all primitive overloads.
