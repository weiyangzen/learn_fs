
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementPolicyDebugLoggingBuilder.java

## Purpose
This test verifies that `BlockPlacementPolicyDefault.chooseRandom` remains stable when block-placement logging level changes dynamically during selection. It targets debug logging builder behavior rather than placement correctness.

## Important APIs, Types, and Functions
The class extends `BaseReplicationPolicyTest` and selects `BlockPlacementPolicyDefault`. `getDatanodeDescriptors` creates three storages across hierarchical rack paths. The test spies the `replicator`, changes `BlockPlacementPolicy.LOG` from INFO to DEBUG inside mocked `chooseDataNode` answers, and calls `chooseRandom` with a disk storage-type requirement.

## Control Flow and State
`testChooseRandomDynamicallyChangeLogger` seeds `results` with all three storages, creates an empty excluded set, and installs two `doAnswer` hooks: one for `chooseDataNode(scope, excluded)` and one for `chooseDataNode(scope, excluded, StorageType.DISK)`. Each hook changes the logger to DEBUG and returns the first datanode. The final `chooseRandom` call exercises logging code that may have built conditional debug state before or during selection.

## Dependencies and Integration Points
The test relies on the base fixture's NameNode, topology, heartbeat, and default policy setup. It uses Mockito spying, `GenericTestUtils.setLogLevel`, `StorageType`, and `EnumMap` storage-type quotas.

## Risks and Test Signals
The main regression risk is logging code assuming a stable log level and throwing when debug becomes enabled mid-operation. There are no explicit assertions; the signal is absence of exception. That makes the test narrow but important for a previously fragile debug/logging path.
