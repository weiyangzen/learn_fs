# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailureOfSharedDir.java

## Purpose
`TestFailureOfSharedDir` verifies configuration and runtime behavior for HA shared edits directories. It ensures the shared edits dir is treated as required, multiple shared dirs are rejected, shared dirs are ordered before local edits dirs, and runtime failure of the required shared dir prevents unsafe log rolling.

## Important APIs, Types, And Functions
Tests are `testSharedDirIsAutomaticallyMarkedRequired`, `testMultipleSharedDirsFails`, `testSharedDirsComeFirstInEditsList`, and `testFailureOfSharedDir`. They use `FSNamesystem.getRequiredNamespaceEditsDirs`, `FSNamesystem.getNamespaceEditsDirs`, `DFS_NAMENODE_SHARED_EDITS_DIR_KEY`, `DFS_NAMENODE_EDITS_DIR_KEY`, `DFS_NAMENODE_EDITS_DIR_REQUIRED_KEY`, `MiniDFSCluster`, `NNStorage`, and `FileUtil.chmod`.

## Control Flow
The configuration tests create synthetic URI lists and assert required-dir inclusion, rejection of comma-separated shared edits dirs, and ordering of shared then local dirs. The runtime test starts an HA cluster with exit-on-shutdown disabled, makes NN0 active, writes a directory, removes write permission from the shared edits dir, waits for resource checking, verifies the standby remains standby and not in safe mode, then tries `rollEditLog` on the active and expects an `ExitException`.

## State And Persistence
Persistent state includes local and shared NameNode edit directories and their edit-log files. The runtime test mutates filesystem permissions on the shared edits directory and later restores them for cleanup. It inspects local edits dirs to verify they did not roll independently after shared-dir finalization failed.

## Dependencies And Integration Points
This file integrates configuration parsing in `FSNamesystem`, resource checking, NameNode RPC log rolling, shared edit journal ordering, `MiniDFSCluster` shutdown behavior, and `GenericTestUtils.assertGlobEquals`.

## Risks
If shared edits are not required or not synced first, local journals can advance beyond shared journals and break standby catch-up. Runtime permission mutation can affect cleanup if not restored. Assertions depend on exact exception text and edit-file names.

## Test Signals
Signals include expected URI membership/order, exact IOException message for multiple shared dirs, standby remaining out of safe mode during resource unavailability, expected `finalize log segment 1, 3 failed for required journal` exit text, and local edits dirs still containing only `edits_inprogress_0000000000000000001`.
