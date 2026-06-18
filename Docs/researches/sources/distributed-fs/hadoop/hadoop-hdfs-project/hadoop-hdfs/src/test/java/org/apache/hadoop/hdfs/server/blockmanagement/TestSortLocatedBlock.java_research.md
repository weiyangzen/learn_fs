# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSortLocatedBlock.java

Purpose: this JUnit 5 test validates `DatanodeManager.sortLocatedBlocks` for replicated `LocatedBlock` instances when locations have mixed service states. It covers live, stale, slow, stale-and-slow, entering maintenance, decommissioning, and decommissioned DataNodes, with configuration switches controlling whether stale and slow nodes should be avoided for reads.

Important APIs and types: `DatanodeManager`, `DatanodeInfo`, `DatanodeInfoWithStorage`, `LocatedBlock`, `ExtendedBlock`, `DFSConfigKeys`, `DFSTestUtil`, `Time`, and mocked `FSNamesystem`/`BlockManager`. The helper `mockDatanodeManager(boolean avoidStaleDNForRead, boolean avoidSlowDNForRead)` builds a real `DatanodeManager` around mocked NameNode services and a `BlockReportLeaseManager`. `mockDatanodes` constructs seven deterministic DataNodes and mutates their admin, stale, and slow-peer state.

Control flow: each test creates a single located block with an ordered location array, calls `dm.sortLocatedBlocks(null, locatedBlocks)`, then asserts the post-sort location order. `testWithStaleDatanodes` checks live before stale before maintenance before decommissioned. `testAviodStaleAndSlowDatanodes`, `testAviodStaleDatanodes`, `testAviodSlowDatanodes`, and `testWithServiceComparator` exercise the four combinations of stale/slow avoidance flags. Where the comparator intentionally treats two classes equally, assertions allow either order within that equivalence class.

State and persistence: there is no disk persistence. State is held in mutable `DatanodeInfo` objects and the `DatanodeManager` slow-peer set. Staleness is simulated by old monotonic timestamps relative to `DFS_NAMENODE_STALE_DATANODE_INTERVAL`.

Dependencies and integration points: this is a focused integration test of NameNode block-location ordering logic, but it avoids a MiniDFSCluster. It depends on Hadoop test utilities for synthetic DataNode identities and Mockito for the minimal NameNode/BlockManager collaborators required by `DatanodeManager`.

Risks: the test uses `==` for some IP string comparisons instead of `equals`, which works only because the same objects usually flow through sorting. The method names contain `Aviod`, so searches for "Avoid" may miss them. The stale interval constant differs from the configured default units used in one test, so future staleness semantics could make the fixtures fragile.

Test signals: successful execution means the read-location comparator preserves the intended priority tiers and handles decommissioning states after service-state ordering. Failures usually indicate a regression in read avoidance configuration, slow-peer ordering, or admin-state demotion.
