<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalMetrics.java

Purpose: Server-side Hadoop metrics source for one `Journal`.

Important APIs/types/functions: Counters for batches, txns, bytes written, RPC-served txns/bytes, empty RPC responses, lagging batches, and synced edit logs; quantiles for sync latency; stat `RpcRequestCacheMissAmount`; metric getters for journal id, writer/promised epochs, highest txid, lag txns, and last journal timestamp.

Control flow: `create` registers a metrics source named `Journal-<journalId>`. `Journal` increments counters and adds sync latencies during writes, RPC tailing, cache misses, and syncer activity. Getter methods tolerate epoch-read IO failures by returning `-1`.

State and persistence behavior: Metrics are in-memory only and derived from `Journal` persistent/runtime state.

Dependencies/integration: Used by `Journal`; registered with `DefaultMetricsSystem`; consumed by Hadoop metrics sinks and JMX.

Risks: Metrics source names collide for duplicate journal ids in one JVM. Getter IO failures are hidden as `-1`, so dashboards must interpret that as unavailable/error.

Test signals: Verify counter increments on journal writes, lagging writes, RPC cache responses/misses, syncer increments, quantile updates, source naming, and fallback values when epoch files throw IO errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalMetrics.java -->
