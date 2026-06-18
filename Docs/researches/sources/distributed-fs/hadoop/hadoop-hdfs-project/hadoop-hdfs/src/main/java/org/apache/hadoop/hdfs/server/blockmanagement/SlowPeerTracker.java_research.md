<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerTracker.java

## Purpose

`SlowPeerTracker` aggregates DataNode peer-latency outlier reports and exposes current slow-peer evidence as sets, JSON, and a top slow-node list.

## Important APIs and types

The main state is `ConcurrentMap<slowNode, ConcurrentMap<reportingNode, LatencyWithLastReportTime>>`. APIs include `isSlowPeerTrackerEnabled`, `addReport`, `getReportsForNode`, `getReportsForAllDataNodes`, `getJson`, `getSlowNodes`, `setMaxSlowPeersToReport`, and test accessor `getReportValidityMs`. `LatencyWithLastReportTime` stores monotonic timestamp and `OutlierMetrics`.

## Control flow

`addReport` creates the nested map if needed and replaces a reporter's previous metrics. Reads filter each nested map by `now - reportTime < reportValidityMs`, converting live entries to `SlowPeerLatencyWithReportingNode`. JSON/top-node generation uses a min-priority queue ordered by number of valid reporters and keeps the top configured count.

## State and persistence behavior

State is in-memory and concurrent. Stale reports are filtered out but not proactively evicted, so old reporter entries can remain indefinitely. JSON serialization returns null only on Jackson failure; empty state returns `[]`.

## Dependencies and integration points

It integrates with `SlowPeerReports`, `OutlierMetrics`, `DFSConfigKeys`, `Timer`, Jackson, Guava primitives/immutable maps, DataNode heartbeat reports, and NameNode/DataNode diagnostics.

## Risks and edge cases

Top-N ordering is by number of reports, not latency magnitude. Ties are priority-queue dependent. Stale reports can accumulate. If `maxNodesToReport` is zero, no nodes are reported. Logging `getSlowNodes` at warn level can be noisy in clusters with persistent slow reports.

## Test signals

Tests should cover report replacement by same reporter, stale filtering, all-node map filtering, JSON schema, top-N by vote count, zero/negative max settings, and disabled subclass parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerTracker.java -->
