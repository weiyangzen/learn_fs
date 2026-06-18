# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockUnderConstructionFeature.java

## Purpose
`TestBlockUnderConstructionFeature` checks the selection of lease-recovery targets for an under-construction block. It verifies that block recovery rotates or selects datanodes according to recovery attempt and recent heartbeat state.

## Important APIs, Types, and Functions
The test uses `BlockUnderConstructionFeature.initializeBlockRecovery`, `BlockInfoContiguous`, `BlockUCState.UNDER_CONSTRUCTION`, `DatanodeStorageInfo`, `DatanodeDescriptor`, `GenerationStamp`, and `DFSTestUtil.resetLastUpdatesWithOffset`.

## Control Flow
The single test creates three datanode storage infos, marks the datanodes alive, creates a contiguous block, and converts it to under-construction state with all three storages. It runs four recovery attempts. Before each attempt it adjusts the datanodes' last-update times, calls `initializeBlockRecovery`, then pulls the lease recovery command from the expected datanode and checks that the target block is the under-construction block.

## State and Persistence Behavior
State is entirely in memory: datanode liveness, monotonic update timestamps, block under-construction feature state, and queued lease-recovery commands. There is no MiniDFSCluster or persisted namespace state.

## Dependencies and Integration Points
The test directly covers block-management internals rather than client APIs. It integrates `BlockInfoContiguous` under-construction conversion with datanode descriptor recovery queues.

## Risks and Edge Cases
The key risk is repeatedly selecting an unhealthy or stale replica for recovery, which can slow or block lease recovery. The final attempt resets heartbeat timestamps and confirms the most recent heartbeat can be selected again.

## Test Signals
Each recovery attempt asserts that the expected datanode's `getLeaseRecoveryCommand(1)` returns the same `BlockInfo` instance, providing a direct signal that the recovery command was queued on the intended datanode.
