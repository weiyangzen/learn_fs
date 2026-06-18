<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSXAttrBaseTest.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSXAttrBaseTest.java

Purpose: JUnit 5 base suite for HDFS NameNode extended attribute APIs. It exercises create, replace, set, get, list, remove, rename, raw namespace behavior, ACL-driven access, and the `security.hdfs.unreadable.by.superuser` special xattr across edit-log replay and fsimage checkpoint reload.

Important APIs/types/functions: static cluster fixtures use `MiniDFSCluster`, `HdfsConfiguration`, `DistributedFileSystem`, `Path`, `XAttrSetFlag`, `UserGroupInformation`, and `FsPermission`. Test helpers include `createFileSystem()`, `createFileSystem(UserGroupInformation)`, `initCluster(boolean)`, `restart(boolean)`, `verifySecurityXAttrExists()`, and `verifyFileAccess()`. The suite also uses `NameNodeAdapter.enterSafeMode()` and `saveNamespace()` to force fsimage persistence.

Control flow: `@BeforeAll` enables xattrs and ACLs, sets small per-inode and per-xattr limits, and starts one DataNode. `@BeforeEach` allocates unique normal and `/.reserved/raw` paths. Mutation tests set xattrs, validate maps/lists and error cases, restart without checkpoint for edit-log replay, then restart with checkpoint for fsimage coverage. Permission tests run operations as synthetic users and expect either `AccessControlException`, `RemoteException`, or successful access depending on path mode and ACLs.

State and persistence: persistent state is HDFS inode xattr metadata stored in edit logs and fsimage. Tests deliberately verify cleanup after xattr removal, rename retention, null-value normalization to empty byte arrays, raw namespace visibility only through raw paths, and the special security xattr's non-removable/no-value semantics.

Dependencies and integration points: integrates NameNode xattr enforcement, ACL permission checks, raw reserved paths, WebHDFS-compatible exception behavior, edit-log replay, checkpointing, and `DFSTestUtil` file creation.

Risks and test signals: important risks are namespace filtering mistakes, permission bypasses, max-count/size regressions, raw xattr leakage, and loss of xattrs after restart. Test signals are successful restart/checkpoint assertions, exact xattr map contents, expected exception text, and access behavior for superuser vs non-superuser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSXAttrBaseTest.java -->
