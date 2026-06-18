# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestComputeInvalidateWork.java

## Purpose
`TestComputeInvalidateWork` verifies how `BlockManager.computeInvalidateWork` schedules deletion work for contiguous replicas and erasure-coded striped blocks. It also checks that invalidation work is skipped or removed when datanodes reformat or re-register with new identities.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `FSNamesystem`, `BlockManager`, `DatanodeManager`, `InvalidateBlocks`, `LocatedStripedBlock`, `SystemErasureCodingPolicies.XOR_2_1_POLICY_ID`, `BlockManagerTestUtil.stopRedundancyThread`, and `Whitebox`. Helpers include `setup`, `teardown`, and `verifyInvalidationWorkCounts`.

## Control Flow
Setup starts a three-datanode cluster, stops the redundancy thread for deterministic behavior, enables an XOR EC policy, creates a striped file, and records the first `LocatedStripedBlock`. The replica, striped, and mixed invalidation tests add more than three times the per-datanode invalidate limit to each datanode under the block-manager write lock, then call `computeInvalidateWork` with varying node limits. Reformat and re-registration tests mutate datanode UUIDs and registrations to ensure stale invalidation work is skipped or removed.

## State and Persistence Behavior
State includes the block-manager invalidation queues, counts split between replica and EC invalidations, datanode UUID registration mappings, and deleted-block queues populated when files are deleted while datanodes are shut down.

## Dependencies and Integration Points
The file integrates EC file creation, namenode block-manager invalidation queues, datanode registration, datanode shutdown, block deletion marking, and white-box access to internal `InvalidateBlocks`.

## Risks and Edge Cases
Important edge cases are fairness and limits across datanodes, mixed replica/EC queues, old datanode UUIDs after reformat, and dead datanodes re-registering with different IDs while invalidations are pending.

## Test Signals
Assertions compare computed work counts against the invalidate limit, verify zero pending deletion after UUID replacement, and check that `InvalidateBlocks` replica and EC counts decrease predictably as datanodes re-register.
