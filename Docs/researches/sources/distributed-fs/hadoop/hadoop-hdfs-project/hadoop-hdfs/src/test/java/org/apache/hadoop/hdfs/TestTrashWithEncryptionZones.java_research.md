# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestTrashWithEncryptionZones.java

Purpose: Tests Trash behavior inside non-Kerberos HDFS encryption zones using a local Java keystore provider.

Important APIs and types: `JavaKeyStoreProvider`, `HdfsAdmin.createEncryptionZone`, `CreateEncryptionZoneFlag.NO_TRASH`, `PROVISION_TRASH`, `FsShell`, `ToolRunner`, `FileSystemTestWrapper`, `DFSTestUtil.verifyDelete`, `DFSTestUtil.createKey`, and `UserGroupInformation.doAs`.

Control flow: `setup` builds a MiniDFSCluster with Java key provider path, delegation-token forcing, small EZ list batch size, and Trash interval of one minute, then creates the test key and shell. `testDeleteWithinEncryptionZone` creates an EZ with provisioned trash, creates an encrypted file, and verifies file and directory delete move through Trash. `testDeleteEZWithMultipleUsers` creates an EZ without provisioned trash, makes it world-writable, has a non-admin user create/delete a file into per-user EZ trash, verifies that user cannot delete the whole EZ, then recreates shell as the original user and deletes the zone.

State and persistence behavior: State includes the local JKS file in the test root, HDFS EZ metadata, trash directories under EZs, and per-user ownership/permissions. It is removed when the cluster/test root is torn down.

Dependencies and integration points: Integrates key provider flushing, encryption-zone metadata, FsShell delete semantics, Trash path selection, UGI user ownership, and NameNode EZ deletion permission checks.

Risks and test signals: The client key provider is explicitly pointed at the NameNode provider for JKS flushing; without that, key updates can be stale. Passing signals Trash works correctly for EZ contents and protects multi-user EZ deletion.
