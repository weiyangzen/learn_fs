<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerDisabledTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerDisabledTracker.java

## Purpose

`SlowPeerDisabledTracker` is the no-op implementation used when DataNode peer statistics are disabled.

## Important APIs and types

It subclasses `SlowPeerTracker` and overrides `isSlowPeerTrackerEnabled`, `addReport`, `getReportsForNode`, `getReportsForAllDataNodes`, `getJson`, and `getSlowNodes`. It returns immutable empty collections or null JSON and logs trace messages pointing to `dfs.datanode.peer.stats.enabled`.

## Control flow

Construction still calls the superclass constructor, but all public behavior short-circuits. Add and retrieval methods do not mutate or expose superclass report state.

## State and persistence behavior

No slow-peer state is recorded by this disabled variant. Any superclass state initialized by construction remains unused.

## Dependencies and integration points

It integrates with configuration selection of slow peer tracking and preserves the `SlowPeerTracker` API contract for callers that do not want to branch on enablement.

## Risks and edge cases

Because it extends the real tracker, constructor-side configuration or future superclass behavior still runs. `getJson` returns null rather than an empty JSON array, so consumers must already tolerate null from the enabled tracker on serialization failure.

## Test signals

Tests should verify disabled flag, no mutation after `addReport`, empty retrievals, null JSON, empty slow-node list, and caller behavior when switching between enabled and disabled trackers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerDisabledTracker.java -->
