# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSTrash.java

## Purpose
Tests Trash behavior on HDFS, including shell trash operations, non-default FS configuration, permissions, empty directory moves, deleting trash directories, and duplicate inode names in trash paths.

## APIs and Control Flow
`setUp` creates a two-DN cluster, initializes world-writable test and trash roots, and creates test users. Simple tests delegate to `TestTrash` helpers. `testDeleteTrash` logs in as user1 and user2, moves per-user temp dirs to isolated trash roots, verifies a user can delete own trash and cannot delete another user's trash, checking the denied message includes the username. `getPerUserTrash` uses a Mockito spy to override `FileSystem.getTrashRoot`. `testDeleteToTrashWhenInodeNameDuplicate` moves a file and a nested directory with duplicate path component names into trash.

## State, Dependencies, Integration
State includes HDFS permissions, trash roots, user identities, and moved namespace entries. Dependencies include `Trash`, `TestTrash`, `DFSTestUtil.login`, `UserGroupInformation`, `FsPermission`, `FsAction`, `AccessControlException`, and Mockito. It integrates public trash APIs with HDFS permission enforcement.

## Risks and Test Signals
Signals are successful delegated helper checks, existence/deletion assertions, and denied access containing the username. Risks include static `fs` being reassigned across tests, mocked trash-root behavior masking real root selection, and test isolation relying on unique UUID trash paths.
