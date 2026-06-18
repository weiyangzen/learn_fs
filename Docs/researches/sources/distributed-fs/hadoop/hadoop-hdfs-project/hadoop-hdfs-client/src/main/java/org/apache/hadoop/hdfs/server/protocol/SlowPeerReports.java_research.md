# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/SlowPeerReports.java

Purpose: `SlowPeerReports` carries DataNode-reported diagnostics about peer DataNodes that appear slow, keyed by peer DataNode UUID and valued by `OutlierMetrics`.

Important APIs/types/functions: `EMPTY_REPORT` is the no-entry sentinel. `create(Map)` returns the sentinel for null/empty maps. `getSlowPeers()`, `haveSlowPeers()`, `equals`, and `hashCode` expose and compare the report.

Control flow: DataNode metrics code constructs reports and sends them to NameNode, where values should be treated as opaque diagnostics rather than cross-node comparable metrics.

State and persistence behavior: final map reference but no defensive copy; contents are mutable if the caller's map is mutable.

Dependencies and integration points: depends on shaded Guava `ImmutableMap`, `OutlierMetrics`, and DataNode heartbeat/report protocol conversion.

Risks and test signals: map mutability can affect equality and report contents after creation. Tests should cover sentinel behavior, equality/hash, and conversion of `OutlierMetrics` through the wire representation.
