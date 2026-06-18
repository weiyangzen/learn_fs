<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlockRetry.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlockRetry.java

Purpose: regression coverage for addBlock retry races and retry-after-restart behavior.

Important APIs/types/functions: uses NameNode RPC `create`, `addBlock`, and `getBlockLocations`; internal `FSDirWriteFileOp.validateAddBlock()`, `chooseTargetForNewBlock()`, and `storeAllocatedBlock()`; `FSNamesystem` locks; Mockito `FSPermissionChecker`; and helper `checkFileProgress()`.

Control flow: `testRetryAddBlockWhileInChooseTarget()` manually runs the first addBlock through validation and target selection, pauses before storing, runs a second full RPC addBlock, then resumes the first store and asserts both return the same block and one located block with expected replication. `testAddBlockRetryShouldReturnBlockWithLocations()` allocates a block, restarts the NameNode, retries addBlock, and checks the same block is returned with locations reselected.

State and persistence: tests live block allocation, blocks map state, and edit-log replay across restart. Locations are intentionally not persisted, so retry must reconstruct them.

Dependencies and integration points: covers `FSDirWriteFileOp`, `FSNamesystem` locking/progress checks, block placement targets, NameNode RPC semantics, and `LocatedBlocks`.

Risks and test signals: risks are duplicate block allocation, missing locations after retry, and races between validation and storage. Signals are block identity equality, single located block, replication count, and file-progress success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlockRetry.java -->
