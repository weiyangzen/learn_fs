# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DataNodeUsageReport.java

Purpose: `DataNodeUsageReport` is a private/unstable value object for DataNodes to report throughput and operation timing metrics to the NameNode.

Important APIs/types/functions: fields include bytes written/read per second, write/read time deltas, blocks written/read per second, and timestamp. `EMPTY_REPORT` is the preferred sentinel for no data. The nested `Builder` offers fluent setters and `build()`. Getters expose all metrics. `equals`, `hashCode`, and `toString` support comparison and diagnostics.

Control flow: callers build reports from sampled counters, often via `DataNodeUsageReportUtil`, then include them in heartbeat/report protocol messages.

State and persistence behavior: effectively immutable after builder construction, though fields are not final and the package-private no-arg constructor supports default/sentinel creation. No persistence; values are serialized through surrounding protocol layers.

Dependencies and integration points: integrates with DataNode-to-NameNode usage reporting and diagnostics. It has no external library dependencies beyond annotations.

Risks and test signals: `hashCode()` collapses long sums into int and is suitable only for hash collections, not uniqueness. Tests should cover builder field assignment, `EMPTY_REPORT`, equality/hash consistency, and string output for diagnostics.
