# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSPermission.java

Purpose: This extensive permission test validates HDFS POSIX-style permission setting, ownership changes, access checks, trash protection, denial messages, and operation-specific permission requirements for owner, group, other, and superuser identities.

Important APIs/types/functions: `FsPermission`, `FsAction`, `FileSystem.access`, `setPermission`, `setOwner`, `Trash`, `UserGroupInformation`, `DFSTestUtil.login/updateConfWithFakeGroupMapping`, `AccessControlException`, `PermissionGenerator`, `PermissionVerifier`, and verifier subclasses for create, open, replication, times, stats, list, rename, and delete.

Control flow: Static setup enables permissions, installs fake user-group mappings, and creates test UGIs. Each test starts a three-DataNode MiniDFSCluster. `testPermissionSetting` iterates randomized umasks and verifies create/mkdir permissions. `testOwnership` checks superuser and owner/group constraints. `testPermissionChecking` builds many ancestor/parent/file/dir combinations with randomized modes, then runs the same operation matrix as USER1, USER2, USER3, and SUPERUSER. Access tests verify owner/group/other masks and exception messages. Trash and non-directory ancestor tests check denial cause/message quality and information hiding.

State and persistence behavior: The tests create real HDFS namespace trees, files, ownership, permissions, trash roots, and per-user FileSystem instances. The permission matrix repeatedly mutates inode modes and ownership while verifier classes compute expected required masks from identity role and operation type.

Dependencies and integration points: It covers NameNode permission enforcement, FileSystem client APIs, fake group mapping, Trash move semantics, content-summary/list/stat paths, and recursive delete semantics for non-empty directories.

Risks and test signals: Signals include exact mode values, owner/group equality, expected allow/deny outcomes, non-AccessControlException for nonexistent files, and denial messages containing or hiding user/path details as appropriate. Risks include randomized coverage size, shared static configuration mutation, and high runtime from the operation matrix.
