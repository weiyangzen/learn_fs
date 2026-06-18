# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSortLocatedStripedBlock.java

Purpose: this test validates sorting of `LocatedStripedBlock` locations when erasure-coded block groups include decommissioned and stale DataNodes. It specifically guards the extra bookkeeping needed for striped blocks: after sorting locations, the parallel block-index and block-token arrays must be reordered consistently with their DataNode entries.

Important APIs and types: `LocatedStripedBlock`, `LocatedBlock`, `DatanodeManager`, `DatanodeInfo.AdminStates`, `ErasureCodingPolicy`, `StorageType`, `BlockTokenIdentifier`, `Token`, `StripedFileTestUtil`, and `DFSTestUtil`. Static setup creates a real `DatanodeManager` with stale-node avoidance enabled. Helper methods build synthetic striped block groups from the default EC policy, with deterministic local DataNode ports matching logical block indices.

Control flow: each test prepares lists of decommissioned logical block indices and replacement target indices, creates two located striped block groups, snapshots each location's block index and token, calls `dm.sortLocatedBlocks(null, lbs)`, then checks two invariants. First, normal/stale-valid locations must appear before decommissioned entries. Second, the location-to-index and location-to-token mapping must remain unchanged even though arrays are permuted. Covered scenarios include multiple decommissioned nodes, duplicate decommissioning for the same block index, fewer-than-full-stripe groups, missing replacement targets, and extra in-service stale targets.

State and persistence: all state is in memory. The block group uses synthetic `ExtendedBlock` metadata, arrays of storage IDs/types, and mutable `DatanodeInfo` admin/timestamp state. No MiniDFSCluster or disk state is involved.

Dependencies and integration points: this test integrates the replicated block-location sorter with striped-block-specific arrays and EC policy dimensions. It relies on the production `DatanodeManager` comparator and on `LocatedStripedBlock` internal array layout staying aligned across locations, indices, and tokens.

Risks: the fixture mutates `List<Integer>` by removing boxed integers and relies on deprecated `new Integer(...)` style to force value removal; changing to index removal would break intent. The tests focus on decommissioned and stale placement, not slow peers for striped blocks. Token assertions are strong because the default block-token array values are identity-sensitive to position.

Test signals: passing tests indicate decommissioned striped-block replicas are demoted without corrupting block-index/token alignment. Failures can imply client-side EC reads may contact poor targets or use a token/index for the wrong internal block.
