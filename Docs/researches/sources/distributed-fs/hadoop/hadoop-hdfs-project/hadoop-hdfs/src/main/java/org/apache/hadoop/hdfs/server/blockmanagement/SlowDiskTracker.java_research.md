<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowDiskTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowDiskTracker.java

## Purpose

`SlowDiskTracker` aggregates slow-disk outlier reports received from DataNode heartbeats and publishes a bounded JSON report of the disks with highest observed latency.

## Important APIs and types

The tracker stores `diskIDLatencyMap` keyed by `datanodeId:disk`, a volatile `slowDisksReport`, report interval/validity settings, and an async-update guard. `DiskLatency` is the Jackson-serializable DTO with `SlowDiskID`, per-operation latency map, timestamp, `getMaxLatency`, and per-op lookup. APIs include `addSlowDiskReport`, `checkAndUpdateReportIfNecessary`, `updateSlowDiskReportAsync`, and `getSlowDiskReportAsJsonString`.

## Control flow

DataNode reports are copied into `DiskLatency` entries with the current monotonic timestamp. On interval expiry, an update thread computes top-N valid disks using a min-priority queue ordered by maximum latency, stores stale entries for cleanup, publishes the volatile report list, removes old reports by identity, and clears the update-in-progress flag.

## State and persistence behavior

State is in-memory and concurrent. Reports expire after three outlier intervals by default. JSON output is derived from the last async report snapshot and returns null when empty or serialization fails.

## Dependencies and integration points

It depends on `SlowDiskReports`, `DiskOp`, `DFSConfigKeys`, `Timer`, Jackson, Guava helpers, `SubjectInheritingThread`, and NameNode/DataNode heartbeat monitoring.

## Risks and edge cases

Async update failures could leave `isUpdateInProgress` true because the runnable has no `finally`. The output ordering is priority-queue iteration order, not sorted descending. Stale cleanup only happens during update. `new ArrayList(ImmutableList.of())` uses a raw type.

## Test signals

Tests should cover report ID construction, top-N selection, stale expiration and cleanup, JSON serialization, update interval gating, concurrent update suppression, and latency-per-operation fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowDiskTracker.java -->
