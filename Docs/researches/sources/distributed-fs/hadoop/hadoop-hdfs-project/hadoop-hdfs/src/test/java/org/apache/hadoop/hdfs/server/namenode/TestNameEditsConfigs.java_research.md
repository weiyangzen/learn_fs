# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameEditsConfigs.java

## Purpose
Integration tests for combinations of NameNode image directories, edits directories, checkpoint directories, required edits dirs, and failure scenarios. The suite validates that NameNode and SecondaryNameNode can migrate between shared and separate storage layouts without reading stale metadata.

## Important APIs, Types, and Functions
- Configures `DFS_NAMENODE_NAME_DIR_KEY`, `DFS_NAMENODE_EDITS_DIR_KEY`, `DFS_NAMENODE_CHECKPOINT_DIR_KEY`, `DFS_NAMENODE_CHECKPOINT_EDITS_DIR_KEY`, and `DFS_NAMENODE_EDITS_DIR_REQUIRED_KEY`.
- Uses `MiniDFSCluster.Builder.manageNameDfsDirs(false)`, `format(false)`, `SecondaryNameNode`, `doCheckpoint`, and `DFSTestUtil.createFile`.
- Inspects storage with `FSImageTestUtil.inspectStorageDirectory`, `assertParallelFilesAreIdentical`, `assertSameNewestImage`, `FSImageTransactionalStorageInspector`, and `FileJournalManager.matchEditLogs`.
- Helpers `checkFile`, `cleanupFile`, and `checkImageAndEditsFilesExistence` validate namespace content and storage files.

## Control Flow
- `testNameEditsConfigs` starts with a shared name+edits dir, checkpoints, adds separate name and edits dirs, checkpoints again, removes shared dirs, then reintroduces them after deleting stale current dirs and verifies only latest metadata is used.
- `testNameEditsRequiredConfigs` verifies a required edits dir not present in edits dirs fails, while required-and-present and optional edits dirs succeed.
- `testNameEditsConfigsFailure` simulates shared-to-split migration, then verifies startup fails when latest edits are missing but succeeds when latest edits can replay from an older shared image.
- `testCheckPointDirsAreTrimmed` supplies whitespace-padded checkpoint dir values and verifies directories are created after checkpoint.

## State and Persistence Behavior
- Heavily validates real on-disk NameNode and SecondaryNameNode storage under a test `dfs` directory.
- File existence across restarts proves fsimage/edit-log replay selected the correct directories.
- Checkpointing propagates images/edits to secondary storage dirs.
- Storage current dirs are deleted/recreated to prevent stale metadata reads.

## Dependencies and Integration Points
- Integrates NameNode startup/restart, storage directory role classification, edit-log replay, SecondaryNameNode checkpointing, file namespace operations, and storage inspection utilities.

## Risks and Edge Cases
- Multi-stage tests are long and stateful; failures can cascade if a prior cluster shutdown/cleanup fails.
- Exact expectations depend on storage file naming and checkpoint behavior.
- `fileSys.close`, `cluster.shutdown`, and `secondary.shutdown` are called in many finally blocks and assume successful initialization.

## Test Signals
- Strong signal for metadata directory migration, required edits validation, stale storage avoidance, checkpoint dir trimming, and replay correctness across name/edit dir layout changes.
