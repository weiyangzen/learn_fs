# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNStorageRetentionFunctional.java

## Purpose
Functional `MiniDFSCluster` coverage for `NNStorageRetentionManager` when multiple `NAME_AND_EDITS` directories exist and one directory fails image saving. It checks that image and edits failure states are decoupled for retention/purging.

## Important APIs, Types, and Functions
- Uses `NNStorage.getImageFileName`, `getFinalizedEditsFileName`, and `getInProgressEditsFileName`.
- Configures `DFS_NAMENODE_NUM_EXTRA_EDITS_RETAINED_KEY` and `DFS_NAMENODE_NAME_DIR_KEY`.
- Uses `NameNode.getRpcServer().setSafeMode` and `saveNamespace`.
- Verifies directory contents with `GenericTestUtils.assertGlobEquals`.
- Simulates storage failure through `FileUtil.chmod(current, "000")`.

## Control Flow
- Starts a zero-DataNode cluster with two manually managed name dirs.
- Calls `doSaveNamespace` repeatedly to produce images and finalized/in-progress edits at known transaction IDs.
- After two successful saves, chmods the first current dir unreadable/unwritable, saves namespace, restores permissions, and asserts failed dir retained old files while healthy dir purged and advanced.
- On the next save, asserts the failed dir can purge logs but not images because image storage remains failed.
- Finally restores permissions and shuts down.

## State and Persistence Behavior
- Directly validates on-disk `current` directory contents for `fsimage_*`, finalized `edits_*`, and `edits_inprogress_*`.
- Exercises NameNode storage failure bookkeeping across multiple saveNamespace calls.
- Retention behavior depends on transaction ID progression and extra edits retained set to zero.

## Dependencies and Integration Points
- Integrates real NameNode storage directories, safe mode save namespace RPCs, retention manager, filesystem permissions, and mini-cluster lifecycle.

## Risks and Edge Cases
- `chmod 000` may behave differently on platforms/filesystems that do not enforce POSIX permissions.
- Exact transaction IDs in assertions couple the test to edit-log progression during saveNamespace.
- The finally block attempts chmod even if directory setup failed.

## Test Signals
- High-value functional signal for retention after partial storage failure and for decoupled image-versus-edits failed states.
