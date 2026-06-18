# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLocatedBlocksRefresher.java

## Purpose
Tests `LocatedBlocksRefresher`, the DFS client background mechanism that refreshes cached block locations for tracked input streams when local dead nodes appear.

## APIs and Control Flow
`setUp` configures replication, block size, prefetch size, disables short-circuit reads, and leaves cluster creation to `setupTest`, which sets the refresh interval and unique client context. `testDisabledOnZeroInterval` expects no refresher. `testEnabledOnNonZeroInterval` expects a refresher and no refreshes without tracked streams. `testRefreshOnDeadNodes` creates a multi-block file, opens a `DFSInputStream`, checks prefetch count, registers it with the refresher, stops a DN hosting the first block, reads to mark a local dead node, waits for one refresh, verifies `locatedBlocks` object changed and dead nodes cleared, repeats with another stopped DN, then deregisters. Helpers stop hosting DNs, wait for run/refresh counters, and create a test file.

## State, Dependencies, Integration
State includes DFS client cached `LocatedBlocks`, local dead-node maps, refresher run/refresh counters, stopped DNs, and client context identity. Dependencies include `LocatedBlocksRefresher`, `DFSInputStream`, `MiniDFSCluster`, `DataNodeProperties`, `HdfsClientConfigKeys`, and `Time`. It integrates background client refresh with read failure handling.

## Risks and Test Signals
Signals are refresher nullability, tracked-stream state, run/refresh count deltas, changed block-location object identity, and cleared dead nodes. Risks are timing-based waits, stopping DNs by transfer address, prefetch count assumptions, and possible extra refreshes if dead locations remain in replicas.
