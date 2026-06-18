## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRollingAverages.java

Purpose: Maintains rolling average metrics for named operations over multiple scheduled windows.

Important APIs/types/functions: Constructor sets metric value naming and schedules a `RatesRoller`; `add(name,value)` records values in per-name `MutableRate`; `collectThreadLocalStates`, `snapshot`, `getStats(minSamples)`, `setRecordValidityMs`, and `close` manage rolling state.

Control flow: A scheduled roller snapshots current rates into a collector, extracts sum/count, appends `SumAndCount` windows per name, and removes old windows. `snapshot` emits average gauges for names with valid rolled data. `getStats` returns averages when sample counts meet a threshold.

State and persistence: Maintains current rates, rolling window queues, scheduled executor/future, metric metadata, and validity period. In-memory only; `close` cancels background work.

Dependencies/integration: Created by registry/annotation factory and uses `MetricsCollectorImpl`, `MetricsRecordBuilder`, mutable rates, and scheduled executor utilities.

Risks/test signals: Background rollover timing, cleanup of stale windows, close behavior, and average calculation are high risk. Tests should use controlled timing and cover no-sample windows and minimum sample thresholds.
