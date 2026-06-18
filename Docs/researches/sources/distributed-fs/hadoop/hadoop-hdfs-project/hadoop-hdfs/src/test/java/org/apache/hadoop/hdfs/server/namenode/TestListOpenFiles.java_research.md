# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestListOpenFiles.java

## Purpose
Integration tests for NameNode open-file listing over RPC, DFSAdmin, HA failover, path filtering, invalid path validation, and robustness when leased files disappear from the inode map.

## Important APIs, Types, and Functions
- Exercises `NamenodeProtocols.listOpenFiles`, `OpenFilesIterator.OpenFilesType`, `OpenFileEntry`, `BatchedRemoteIterator.BatchedEntries`, and DFS client `listOpenFiles`.
- Uses `DFSTestUtil.createOpenFiles`, `closeOpenFiles`, and `createFile`.
- HA test uses `MiniDFSNNTopology.simpleHATopology`, `HATestUtil`, `HAUtil.getProxiesForAllNameNodesInNameservice`, `DFSAdmin -listOpenFiles`, and active/standby transitions.
- Direct deletion edge case uses `FSNamesystem.writeLock(RwLockMode.FS)`, `FSDirectory.removeFromInodeMap`, and `leaseManager.removeLease`.

## Control Flow
- `setUp` starts a 3-DataNode cluster with heartbeat interval 1 and list-open-files batch size 5.
- `testListOpenFilesViaNameNodeRPC` validates empty lists, adds open files across several batch sizes, repeatedly lists with last-entry IDs, closes files incrementally, and verifies no blocking-decommission entries.
- `verifyOpenFiles` loops over batched RPC responses until `hasMore` is false, removing expected paths from a set.
- `testListOpenFilesInHA` runs `DFSAdmin -listOpenFiles` repeatedly in a background `SubjectInheritingThread`, shuts down active NN0, transitions NN1 active, and verifies no client-side listing error.
- `testListOpenFilesWithFilterPath` validates prefix filtering for `/base` and `/base/` versus similarly named `/base-open`.
- Invalid path tests distinguish server-side absolute-path checks from client-side wrong-filesystem checks.
- Deleted-path test removes an inode from the inode map while a lease remains and asserts listing does not throw `NullPointerException`.

## State and Persistence Behavior
- Open-file state is live lease/under-construction state held by NameNode, not persisted across these tests.
- HA test depends on active NameNode state and failover configuration; open files are created before failover listing.
- Deleted-path test mutates in-memory inode map under write lock to simulate inconsistency between lease manager and directory state.

## Dependencies and Integration Points
- Integrates NameNode RPC, DFSAdmin CLI, DFS client, HA failover utilities, lease manager, FSDirectory, and FSNamesystem locks.
- Uses `DFS_NAMENODE_LIST_OPENFILES_NUM_RESPONSES` to force pagination.
- Uses `LambdaTestUtils.intercept` to assert exception type/message.

## Risks and Edge Cases
- HA background thread has timing windows around failover and command execution.
- Direct inode-map removal is intentionally invasive and must hold the correct lock to avoid race/NPE behavior.
- Filtering semantics depend on exact server path normalization.
- The test assumes no open files are blocking decommission unless explicitly created for that type.

## Test Signals
- Good signal for batched listing correctness, no duplicates/missing paths, HA command resilience, path validation, and stale lease/inode inconsistency safety.
