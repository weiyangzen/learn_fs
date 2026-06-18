# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestAclWithSnapshot.java

Purpose: Verifies ACL behavior across HDFS snapshots, including immutable snapshot ACLs, permission enforcement, restart/checkpoint persistence, snapshot-path mutation rejection, quota edge cases, and `AclFeature` deduplication/reference counting.

Important APIs/types/functions: static users `BRUCE` and `DIANA` drive authorization checks through `DFSTestUtil.getFileSystemAs`. Tests use `hdfs.setAcl`, `modifyAclEntries`, `removeAcl`, `removeAclEntries`, `removeDefaultAcl`, `getAclStatus`, and `AclTestHelpers.assertPermission`. `FSAclBaseTest.getAclFeature`, `AclStorage.getUniqueAclFeatures`, and `AclFeature.getRefCount` inspect internal ACL feature sharing. `restart(boolean checkpoint)` optionally invokes `NameNodeAdapter.enterSafeMode` and `saveNamespace`.

Control flow: each test creates a unique `/pN` and snapshot name. Root/content ACL tests set initial ACLs, create a snapshot, mutate or remove ACLs on the live inode, then assert the live path reflects the new ACL while `.snapshot/name` retains old entries and access results. Assertions are repeated after edit-log restart and checkpoint reload. Mutation-on-snapshot tests expect `SnapshotAccessControlException`.

State and persistence behavior: ACL state is checked before restart, after restart without checkpoint, and after saved namespace reload. Deduplication tests verify snapshot roots can share the same `AclFeature`, mutations create new features for live inodes, and deletion/removal eventually drops reference counts and unique feature entries.

Dependencies and integration points: integrates HDFS ACL config (`DFS_NAMENODE_ACLS_ENABLED_KEY`), NameNode saveNamespace, internal `AclStorage`, and user impersonation.

Risks and test signals: strong regression coverage for immutable snapshot metadata and ACL persistence. Some quota tests only assert that ACL changes/removals succeed under tight namespace quota; they do not assert quota counters directly.
