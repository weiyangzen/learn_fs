# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestRedundancyMonitor.java

## Purpose
`TestRedundancyMonitor` is a focused concurrency regression test for target choice while DataNodes disappear from topology. It verifies that `BlockPlacementPolicyDefault.chooseTarget` does not propagate a runtime failure when the topology becomes empty between rack-count checks and target selection.

## Important APIs, types, and functions
The test uses `MiniDFSCluster`, `BlockManager`, `BlockPlacementPolicyDefault`, `NetworkTopology`, Mockito `spy`, and `GenericTestUtils.DelayAnswer`. It calls `chooseTarget` directly with the default storage policy and `BLOCK_SIZE`, while another thread removes all `DatanodeDescriptor` entries from a spied topology.

## Control flow
The cluster starts with two hosts on the same rack. The test replaces the placement policy's `clusterMap` with a spy and delays `getNumOfNonEmptyRacks`. One executor task enters `chooseTarget`; once the delay confirms the code path is inside topology inspection, another task removes every DataNode from the topology. The delay is released and `chooseTargetFuture.get()` is checked so any exception is rethrown as the test failure.

## State and persistence behavior
Only in-memory topology and heartbeat manager state are involved. No filesystem data is created. The state transition of interest is a concurrent drop from non-empty topology to empty topology during target selection.

## Dependencies and integration points
This test is at the boundary between BlockManager redundancy work and placement policy. It simulates a race that can occur because redundancy monitor invokes choose-target logic outside the global NameNode lock.

## Risks and test signals
The success signal is absence of an exception. There are no assertions on chosen targets because the scenario is intentionally degraded. The risk area is concurrent topology mutation; a regression would often appear as `ArithmeticException` or another runtime exception from rack arithmetic on an empty topology.
