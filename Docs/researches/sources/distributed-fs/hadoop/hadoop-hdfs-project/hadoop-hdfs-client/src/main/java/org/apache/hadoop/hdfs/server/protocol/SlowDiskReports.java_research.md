# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/SlowDiskReports.java

Purpose: `SlowDiskReports` carries DataNode-reported slow disk diagnostics to the NameNode as a map from disk base path to operation latency metrics.

Important APIs/types/functions: `EMPTY_REPORT` is the no-entry sentinel. `create(Map)` returns the sentinel for null/empty input or a new report otherwise. `getSlowDisks()` and `haveSlowDisks()` expose contents. `DiskOp` enumerates `METADATA`, `READ`, and `WRITE`, maps to protocol string values, and can parse via `fromValue`.

Control flow: DataNode callers build a map of disk path to per-operation latency and pass it through heartbeat/report conversion. NameNode should expose the values diagnostically without comparing across DataNodes.

State and persistence behavior: final map reference but no defensive copy; caller mutations can alter the report. No durable state in this class.

Dependencies and integration points: depends on shaded Guava `ImmutableMap` for sentinel and protocol conversion code that maps `DiskOp` names to protobuf reports.

Risks and test signals: mutable map exposure can surprise consumers. `DiskOp.fromValue` returns null for unknown values, requiring callers to guard. Tests should cover null/empty sentinel behavior, equality independent of map identity, disk op string round trips, and protocol conversion with all operation types.
