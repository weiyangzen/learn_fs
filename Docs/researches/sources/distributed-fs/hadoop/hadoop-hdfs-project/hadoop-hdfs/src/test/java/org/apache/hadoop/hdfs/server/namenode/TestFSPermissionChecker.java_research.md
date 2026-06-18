<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSPermissionChecker.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSPermissionChecker.java

Purpose: `TestFSPermissionChecker` is a direct unit suite for ACL-based permission resolution in `FSPermissionChecker`. It cross-validates HDFS ACL behavior against expected POSIX ACL semantics for owners, named users, groups, named groups, masks, traversal denial, default-only ACL entries, and other permissions. It also tests slow access-control-enforcer reporting.

Important APIs, types, and functions: it builds an in-memory `FSDirectory` with a mocked `FSNamesystem`, creates `INodeDirectory` and `INodeFile` objects, updates ACLs via `AclStorage.updateINodeAcl`, resolves paths through `FSDirectory.getINodesInPath`, and invokes `getPermissionChecker(...).checkPermission`. Helper methods are `addAcl`, `assertPermissionGranted`, `assertPermissionDenied`, `createINodeDirectory`, `createINodeFile`, and the slowness check around `FSPermissionChecker.runCheckPermission`.

Control flow: setup mocks `createFsOwnerPermissions` to return immutable permission status for superuser/supergroup, then creates an `FSDirectory`. Each ACL test constructs a small inode tree, attaches ACL entries, then checks grants/denials for synthetic users `bruce`, `diana`, and `clark`. Denial assertions require `AccessControlException` and verify the error message includes the user name and parent path. The final slowness test creates a threshold-aware message function, runs a fast lambda and a sleeping lambda through `runCheckPermission`, and expects null vs non-null messages.

State and persistence behavior: no on-disk persistence; state is in-memory inode metadata, ACL features, current snapshot ID, and user/group identity. It tests permission semantics independently from RPC, edit logs, or cluster setup.

Dependencies and integration points: depends on ACL helper construction, `FSDirectory.DirOp.READ`, inode child attachment, snapshot current-state constants, `INodeAttributeProvider.AccessControlEnforcer` class metadata for slow-check messages, and UGI group membership.

Risks and edge cases: direct inode construction uses `GRANDFATHER_INODE_ID` repeatedly, which is acceptable for permission resolution but not representative of full namespace invariants. Tests are sensitive to exact ACL mask semantics and parent-path text in denial messages. Default ACL entries in traversal tests must not incorrectly influence access ACL resolution.

Test signals: every permission matrix uses explicit grant/deny assertions for compound actions (`READ_WRITE`, `READ_EXECUTE`, `WRITE_EXECUTE`, `ALL`), denial messages must identify the user and parent, and slow enforcer logic must distinguish fast and delayed runners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSPermissionChecker.java -->
