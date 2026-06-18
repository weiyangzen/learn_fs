# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsHdfs.java

## Purpose

`TestViewFsHdfs` runs the FileContext-oriented `ViewFsBaseTest` over HDFS and adds a UGI lazy target initialization check. It is the `FileContext` counterpart to parts of `TestViewFileSystemHdfs`.

## Important APIs, types, and functions

Important APIs are `ViewFsBaseTest`, `FileContext`, `MiniDFSCluster`, `HdfsConfiguration`, `UserGroupInformation.doAs`, `AccessControlException`, `FsPermission`, and `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`. The primary added test is `testTargetFileSystemLazyInitialization`.

## Control flow, state, and persistence

`@BeforeAll` starts HDFS, creates the current user's working directory, and stores an HDFS `FileContext`. In each test `fcTarget` is assigned before inherited setup. The lazy initialization test first creates/deletes `/data/user1` as the current user, then constructs a ViewFs `FileContext` inside a different UGI. The first mkdir fails due to user permissions. After `/data` ownership and permissions are changed, a new UGI-created ViewFs context creates the directory and the owner is asserted as `user1`.

## Dependencies and integration points

This covers FileContext ViewFs mount resolution, target filesystem lazy creation under the creator UGI, HDFS permissions, and inherited token behavior. It validates identity capture at ViewFs construction time, not operation call time.

## Risks and test signals

Risks include initializing target filesystems under the wrong user, caching target contexts across users, or wrong delegation-token count. Signals are the expected initial `AccessControlException`, successful mkdir after permission changes, and resulting owner equal to the alternate UGI short name.
