# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSequentialBlockId.java

## Purpose
`TestSequentialBlockId` validates sequential contiguous block ID allocation, collision recovery when the generator is rewound, legacy versus new block detection by generation stamp, and generation stamp selection for legacy and new blocks.

## Important APIs, types, and functions
The test uses `MiniDFSCluster`, `FileSystem`, `DFSTestUtil.createFile`, `DFSTestUtil.getAllBlocks`, `SequentialBlockIdGenerator`, `BlockIdManager`, and `Block`. Mockito mocks and spies allow direct testing of `BlockIdManager.isLegacyBlock` and `nextGenerationStamp`.

## Control flow
`testBlockIdGeneration` creates a ten-block file in a one-DataNode cluster and asserts each block ID increments by one from the first block. `testTriggerBlockIdCollision` creates one ten-block file, rewinds the sequential block ID generator by five, creates a second ten-block file, and asserts the first block of the second file starts immediately after the last block of the first file rather than colliding. `testBlockTypeDetection` stubs the legacy generation-stamp limit and verifies blocks below or above it are classified correctly. `testGenerationStampUpdate` stubs next legacy and new generation stamp values and verifies `nextGenerationStamp(true/false)` delegates to the right counter.

## State and persistence behavior
The cluster tests use in-memory NameNode block ID generator state and block map collision checks. The mocked tests isolate generation-stamp logic from cluster state. No restart or fsimage persistence is validated.

## Dependencies and integration points
This file tests the ID generation service used during HDFS block allocation and the generation-stamp split used to distinguish legacy blocks. It depends on real file creation for collision detection rather than only testing the generator in isolation.

## Risks and test signals
Signals include exact sequential ID equality, non-colliding start ID after rewind, and boolean/classification outcomes from mocked generation stamps. The tests catch regressions that might allocate duplicate block IDs or misclassify blocks after generation-stamp layout changes.
