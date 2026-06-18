<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclConfigFlag.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclConfigFlag.java

Purpose: verifies that disabling `dfs.namenode.acls.enabled` rejects ACL API operations while still allowing NameNode startup from edits/fsimage containing ACL metadata.

Important APIs/types/functions: uses `MiniDFSCluster`, `DistributedFileSystem`, `DFSConfigKeys.DFS_NAMENODE_ACLS_ENABLED_KEY`, `AclTestHelpers.aclEntry()`, and `NameNodeAdapter` checkpoint helpers. `expectException(Executable)` asserts `AclException` and configuration-key text.

Control flow: individual tests start a cluster with ACLs disabled, create `/path`, and assert `modifyAclEntries`, `removeAclEntries`, `removeAcl`, `setAcl`, and `getAclStatus` fail. Persistence tests first enable ACLs, set an ACL, then restart with ACLs disabled either from edit logs or after saving a checkpoint.

State and persistence: writes ACL metadata to the namespace when enabled, then tests replay/load with ACL support disabled. No final persistent state is needed after teardown.

Dependencies and integration points: covers DFS client ACL APIs, NameNode ACL config gates, edit-log loading, fsimage loading, and safe-mode namespace saving.

Risks and test signals: risks are accidentally allowing ACL mutation/read APIs when disabled or rejecting existing namespace metadata during upgrade/restart. Signals are exact `AclException` failures and successful restarts with stored ACLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclConfigFlag.java -->
