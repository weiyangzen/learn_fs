# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestListCorruptFileBlocks.java

## Purpose
Slow integration tests for the NameNode and DFS client corrupt-file-block listing APIs. The tests create files in a `MiniDFSCluster`, deliberately corrupt or remove block and metadata files on DataNode storage, trigger detection, and validate both server-side counts and client-side iteration/paging.

## Important APIs, Types, and Functions
- Uses `FSNamesystem.listCorruptFileBlocks`, `FSNamesystem.getCorruptFilesCount`, `DistributedFileSystem.listCorruptFileBlocks`, and `CorruptFileBlockIterator.getCallsMade`.
- Creates files via `DFSTestUtil.Builder`, `createFiles`, `waitReplication`, `checkFiles`, and `cleanup`.
- Manipulates storage through `MiniDFSCluster.getFinalizedDir`, `getAllBlockFiles`, `getAllBlockMetadataFiles`, `Block.metaToBlockFile`, `cluster.getInstanceStorageDir`, and raw `RandomAccessFile`/`FileChannel` writes.
- Forces detection using reads that produce `BlockMissingException`, DataNode directory scanner, block report intervals, DataNode restarts, and safe mode transitions.

## Control Flow
- `testListCorruptFilesCorruptedBlock` corrupts bytes near the end of one block file, reads files to trigger detection, and expects one corrupt file.
- `testListCorruptFileBlocksInSafeMode` repeats corruption with safemode/repl-queue settings, restarts the NameNode, waits for replication queues, and verifies corrupt listing still works while safemode remains active.
- `testlistCorruptFileBlocks` deletes all block and metadata files for three files, polls until three corrupt entries appear, then validates cookie-based paging.
- `testlistCorruptFileBlocksDFS` validates the public `DistributedFileSystem` iterator path for the same deletion scenario.
- `testMaxCorruptFiles` creates many one-block files, deletes all blocks, runs scanner/restarts DataNodes, verifies the NameNode response cap, and checks client iteration makes multiple RPC calls.
- `testListCorruptFileBlocksOnRelativePath` sets a working directory and verifies relative path resolution for the DFS client API.

## State and Persistence Behavior
- Corruption is represented by on-disk DataNode block files, block metadata files, and NameNode block state after block reports or read-triggered bad-block reports.
- Safe mode test validates corrupt-block state across NameNode restart while replication queues are repopulating.
- Cookie paging mutates the string-array cookie across server calls.
- Relative path test depends on `FileSystem` working-directory state.

## Dependencies and Integration Points
- Integrates NameNode block manager, DataNode directory scanner, block reports, DFS client iteration, `DFSTestUtil`, and physical storage layout.
- Uses `HdfsClientConfigKeys.Retry.WINDOW_BASE_KEY`, block report intervals, directory scan intervals, and safemode thresholds to reduce wait time and force desired states.
- Tagged `slow`, with long per-test timeouts due to polling and cluster restarts.

## Risks and Edge Cases
- Tests are timing-sensitive around scanner/block-report discovery and include polling loops up to 30 seconds or longer.
- Physical block deletion assumes mini-cluster storage directory layout and number of data directories.
- `testMaxCorruptFiles` relies on default max corrupt files returned and can be expensive because it creates `max * 3` files.
- Direct corruption can surface as expected `BlockMissingException`; other IOExceptions fail the test.

## Test Signals
- Strong end-to-end signal that corrupt file listing is bounded, pageable, path-aware, safe-mode-capable, and accurately reflected in NameNode metrics/counts.
- Covers server API, public DFS API, iterator paging, max-response caps, safemode restart, and relative path behavior.
