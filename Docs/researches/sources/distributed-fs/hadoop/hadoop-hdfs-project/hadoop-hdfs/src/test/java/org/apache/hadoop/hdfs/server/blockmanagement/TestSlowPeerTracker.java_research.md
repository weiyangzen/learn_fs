# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSlowPeerTracker.java

## Purpose
`TestSlowPeerTracker` validates aggregation, expiration, replacement, ranking, and JSON serialization for slow peer reports. These reports identify DataNodes considered slow by other DataNodes and feed the slow-node exclusion machinery used by placement tests.

## Important APIs, types, and functions
The test uses `SlowPeerTracker`, `SlowPeerJsonReport`, `OutlierMetrics`, `FakeTimer`, and Jackson deserialization to `Set<SlowPeerJsonReport>`. Tracker methods under test include `addReport`, `getReportsForAllDataNodes`, `getReportsForNode`, `getReportValidityMs`, and `getJson`. Helper `isNodeInReports` checks serialized slow-node membership.

## Control flow
`testEmptyReports` verifies empty all-node and per-node queries. `testReportsAreRetrieved` adds reports for two slow nodes from different reporters and checks all-node and per-node counts. Expiration tests advance `FakeTimer` to verify all reports disappear after validity, only newer reports survive partial expiration, and an expired report can be replaced by a valid report for the same slow/reporter pair. `testGetJson` verifies JSON contains slow nodes with reports and excludes nodes that only appear as reporters. `testGetJsonSizeIsLimited` adds more candidate slow nodes than the output limit and verifies high-ranked nodes with multiple reports are retained while a lower-ranked node is excluded. `testLowRankedElementsIgnored` confirms five nodes with two reports outrank ten nodes with one report each.

## State and persistence behavior
State is in-memory slow-node-to-reporting-node telemetry with timestamped `OutlierMetrics`. Expiry is purely based on `FakeTimer`; there is no persistence.

## Dependencies and integration points
This tracker supplies slow peer data to `DatanodeManager` and placement policy slow-node exclusion. The JSON ranking behavior is also consumed by NameNode diagnostics and web/API reporting.

## Risks and test signals
Signals include exact counts, absence after expiry, slow-node membership in JSON, reporter latency ordering in serialized reports, and exclusion of low-ranked elements when the report is capped. The deterministic fake clock makes timing stable. Regressions would lose reports too early, retain stale reports, serialize reporters as slow nodes, or rank one-report nodes above stronger multi-report evidence.
