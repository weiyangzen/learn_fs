## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsCollectorImpl.java

Purpose: Concrete collector that accumulates filtered record builders during one source snapshot.

Important APIs/types/functions: `addRecord(MetricsInfo/String)` creates `MetricsRecordBuilderImpl`; `getRecords()` materializes non-null records; `iterator()` exposes builders; `clear()` resets; package setters configure record and metric filters.

Control flow: Record name filtering happens before adding a builder to the list. `getRecords` asks each builder to apply final tag filtering and build immutable records.

State and persistence: Mutable list of builders plus current filters; reused by `MetricsSystemImpl` and cleared between sources.

Dependencies/integration: Used by `MetricsSourceAdapter` and rolling-average internals.

Risks/test signals: Reuse requires `clear()` after every source. Tests should cover record filter rejection, metric filter rejection, and builder iteration.
