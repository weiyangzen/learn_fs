# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DataNodeUsageReportUtil.java

Purpose: `DataNodeUsageReportUtil` converts cumulative DataNode metrics into interval usage reports by comparing current counters with the previous sample.

Important APIs/types/functions: `getUsageReport(...)` accepts cumulative byte, time, block-operation counters and `timeSinceLastReport`; it returns the previous report if the interval is zero, otherwise builds a new `DataNodeUsageReport` with per-second deltas and time deltas. Helper methods calculate bytes/block ops per second and read/write time deltas.

Control flow: on nonzero interval, it builds a report, stores all raw current counters as baselines, stores `lastReport`, and returns the new report. On zero interval, it initializes `lastReport` to `EMPTY_REPORT` if needed and returns it without updating baselines.

State and persistence behavior: mutable in-memory baselines make this utility stateful and intended for single DataNode reporter use. Timestamp uses `Time.monotonicNow()`.

Dependencies and integration points: depends on `DataNodeUsageReport` and Hadoop `Time`. It integrates with heartbeat/report generation.

Risks and test signals: `timeSinceLastReport` is treated as seconds by calculation despite the name not encoding units; callers must pass matching units. Counter resets can produce negative rates. The class is not synchronized. Tests should cover first zero interval, baseline updates, delta math, negative/reset behavior, and repeated calls.
