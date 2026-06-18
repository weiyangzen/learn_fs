## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableMetric.java

Purpose: Abstract base for metrics that accumulate mutable state between snapshots.

Important APIs/types/functions: Declares `snapshot(MetricsRecordBuilder, boolean)`. Provides `changed`, `setChanged`, and `clearChanged` flag helpers.

Control flow: Concrete metrics mark changed on mutation and snapshot either all values or only changed values depending on the `all` flag.

State and persistence: In-memory changed flag; no persistence.

Dependencies/integration: Parent of counters, gauges, stats, rates, quantiles, rolling averages, and method metrics.

Risks/test signals: Changed flag semantics are central. Tests should ensure no-value snapshots are suppressed when `all=false` and unchanged.
