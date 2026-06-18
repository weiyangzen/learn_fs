# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestTrashWithSecureEncryptionZones.java

Purpose: Secure counterpart to encryption-zone Trash tests, using Kerberos MiniKdc, MiniKMS, HTTPS-only HDFS endpoints, and a shared secure MiniDFSCluster.

Important APIs and types: `MiniKdc`, `MiniKMS`, `HdfsAdmin.createEncryptionZone`, `FsShell`, `ToolRunner`, `CreateEncryptionZoneFlag.PROVISION_TRASH`, `KMSClientProvider`, `KeyStoreTestUtil`, `DFSTestUtil.verifyDelete`, and Trash helpers `getCurrentTrashDir`, `-expunge`, `-skipTrash`.

Control flow: Static `init` creates Kerberos principals/keytab, configures secure HDFS/KMS/SSL, writes `kms-site.xml`, starts MiniKMS and MiniDFSCluster, creates the KMS key, and configures `FsShell` with Trash interval 1. Tests validate encrypted-file delete goes to EZ-local Trash, whole-zone delete goes to home Trash, expunge removes encrypted and non-encrypted trash entries, `-skipTrash` bypasses trash, empty directory delete requires `-r`, deleting a file from inside EZ Trash works, and trash files survive NameNode restart.

State and persistence behavior: Uses static cluster, filesystem, shell, counters, KDC, KMS, generated keytab, KMS keystore, and SSL artifacts. `testTrashRetentionAfterNamenodeRestart` explicitly validates Trash metadata persists across NameNode restart.

Dependencies and integration points: Integrates secure HDFS, secure KMS, encryption-zone trash provisioning, shell delete/expunge behavior, user home trash layout, and NameNode restart behavior.

Risks and test signals: Method ordering is fixed by method name, but static counters still avoid path reuse. Security setup is heavyweight and hostname-sensitive. Passing signals secure EZ Trash placement, skip/expunge semantics, and restart retention are correct.
