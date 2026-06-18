# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSequentialBlockGroupId.java

## Purpose
`TestSequentialBlockGroupId` validates allocation and collision handling for erasure-coded block group IDs. It ensures group IDs advance through the striped block group ID space, avoid collisions with existing groups, avoid collisions with legacy contiguous blocks using negative IDs, and reset on BlockManager clear.

## Important APIs, types, and functions
The test uses `SequentialBlockGroupIdGenerator`, `SequentialBlockIdGenerator`, `BlockIdManager`, `BLOCK_GROUP_INDEX_MASK`, `MAX_BLOCKS_IN_GROUP`, `MiniDFSCluster`, `DistributedFileSystem`, `StripedFileTestUtil`, `ErasureCodingPolicy`, and `DFSTestUtil.getAllBlocks`. Mockito `spy`, `doAnswer`, and `Whitebox.setInternalState` replace the regular block ID generator in one collision test.

## Control flow
`setup` starts a MiniDFSCluster sized for the default EC policy plus spare DataNodes, enables the EC policy, creates `/ecDir`, and sets the EC policy on that directory. `testBlockGroupIdGeneration` records the initial generator value, creates an EC file with four block groups, resets the generator to the initial value, repeatedly skips to the next group-aligned value, and asserts each located block group ID matches. It then clears the BlockManager and checks the generator current value is `Long.MIN_VALUE`.

`testTriggerBlockGroupIdCollision` creates one EC file, rewinds the block group generator to its initial value, creates a second EC file, and verifies no block group ID is shared. `testTriggerBlockGroupIdCollisionWithLegacyBlockId` first forces the contiguous `SequentialBlockIdGenerator.nextValue()` to return a value in the block group space, creates a contiguous file with that ID, resets the group generator, creates an EC file, and verifies the EC block group IDs do not collide with the legacy block ID.

## State and persistence behavior
State includes the in-memory generator counters, BlockManager block map, EC directory policy, and allocated block IDs visible through located blocks. The tests do not restart the NameNode, so persistence of generator counters is not exercised.

## Dependencies and integration points
The file integrates ID generators with real file creation for EC and contiguous blocks. It relies on the block group ID layout constants and Whitebox replacement of BlockIdManager internals to force rare collision scenarios.

## Risks and test signals
Signals are exact block group count, expected aligned ID values, uniqueness across files, uniqueness against forced legacy IDs, and reset value after clear. It catches regressions in ID spacing, collision retry loops, and separation between contiguous and striped ID spaces.
