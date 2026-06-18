# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestBlockUnderConstruction.java

## Purpose

`TestBlockUnderConstruction` verifies NameNode metadata consistency for files being written, block-location reads against unclosed files, and block recovery behavior when expected storage IDs no longer resolve.

## Important APIs, Types, and Functions

The class uses a static `MiniDFSCluster` with three datanodes, `DistributedFileSystem`, `FSDataOutputStream`, `DFSClientAdapter`, `NamenodeProtocols.getBlockLocations`, `FSNamesystem`, `INodeFile`, `BlockInfo`, `BlockManager`, `BlockUnderConstructionFeature`, `BlockUCState`, and `commitBlockSynchronization`. Helpers `writeFile` and `verifyFileBlocks` drive block allocation and inspect NameNode internal block state.

## Control Flow

`writeFile` writes a full block using `TestFileCreation.writeFile`, flushes to datanodes, and polls client block locations until the block count increases. `verifyFileBlocks` looks up the inode, checks whether it is under construction as expected, walks all blocks, asserts all but the trailing blocks are complete and registered in the BlocksMap, and checks last-block completion after close. `testBlockCreation` writes five blocks to an open file, verifying consistency after each write and after close. `testGetBlockLocations` writes an unclosed file incrementally and asserts the last returned block is not complete. `testEmptyExpectedLocations` fakes block recovery with an invalid storage ID and verifies subsequent block-location lookup does not throw.

## State and Persistence Behavior

The suite targets live NameNode metadata state: inode under-construction flag, block completion/committed states, BlocksMap identity, located-block responses, generation stamps, and recovery metadata. There is no restart persistence. The invalid-storage scenario models storage failure or datanode reregistration by supplying a nonexistent storage ID during synchronization.

## Dependencies and Integration Points

It integrates client writes/DataStreamer allocation, NameNode block manager internals, inode directory lookup, block recovery initialization, and NameNode RPC block-location APIs. It uses `TestFileCreation` utilities to match expected block size behavior.

## Risks and Edge Cases

The `writeFile` helper ignores its `size` parameter and always writes `BLOCK_SIZE`, so callers passing half-block length still create full-block write behavior while using `len` as the query length. The penultimate-block assertion contains complex boolean logic and is mainly a regression guard for committed/complete transitions. The invalid-storage test tolerates a current `IllegalStateException`, focusing only on avoiding later NPE in block-location lookup.

## Test Signals

Signals include inode `isUnderConstruction` matching file-open state, all inspected blocks present by identity in BlocksMap, closed-file last block complete, unclosed-file final located block incomplete, no crash after `commitBlockSynchronization` with `invalid-storage-id1`, and successful subsequent `getBlockLocations`.
