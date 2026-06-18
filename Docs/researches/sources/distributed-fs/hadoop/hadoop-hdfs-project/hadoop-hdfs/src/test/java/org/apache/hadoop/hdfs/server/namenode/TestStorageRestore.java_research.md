# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStorageRestore.java

## Purpose

`TestStorageRestore` validates NameNode failed-storage restoration for name and edits directories, including checkpoint-driven reactivation, dfsadmin toggling, multiple secondary checkpoint races, and permission-based restore failures.

## Important APIs, Types, and Functions

The fixture configures two image+edits dirs (`name1`, `name2`) and one edits-only dir (`name3`) with `DFS_NAMENODE_NAME_DIR_RESTORE_KEY=true`. Helpers include `invalidateStorage`, which reports storage errors and injects edit-log write faults by spying `EditLogOutputStream`, and `printStorages`. Tests use `FSImage`, `NNStorage`, `JournalSet.JournalAndStream`, `FileJournalManager`, `SecondaryNameNode`, `FSImageTestUtil`, `CLITestCmdDFS`, and `DFSAdmin -restoreFailedStorage`.

## Control Flow

The main restore test starts a cluster and secondary, creates a directory, invalidates selected storage dirs, creates another directory, verifies edits diverge, checkpoints to restore failed dirs, verifies fsimage and edits placement by txid, performs another edit, and confirms all active logs match through clean shutdown. Other tests toggle restore via dfsadmin, simulate an incomplete checkpoint from one secondary followed by a complete checkpoint from another, and remove permissions so restoration fails until permissions are restored.

## State and Persistence Behavior

This class directly inspects and mutates on-disk `current` storage directories, image files, finalized and in-progress edit logs, permissions, and the storage restore flag. It tests whether restored directories keep useful old images but receive fresh log segments and later finalized logs.

## Dependencies and Integration Points

It integrates storage error reporting, edit log journal streams, checkpoint upload/download, SecondaryNameNode behavior, dfsadmin CLI plumbing, and platform-specific permission handling through `Shell.WINDOWS`.

## Risks and Edge Cases

Serving an empty restored directory to a checkpoint client can lose namespace edits. Restoring only some directories can create mismatched edit logs. Permission behavior differs by OS. Fault injection through Mockito spies must target the active current stream.

## Test Signals

Signals include divergent edits before restore, matching `fsimage_4` only in image dirs, missing finalized logs in failed dirs for the old segment, matching new in-progress logs across all dirs, MD5 changes after new edits, dfsadmin output containing `restoreFailedStorage is set to true`, path survival after restart, and storage-dir counts changing from one back to three.
