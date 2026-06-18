# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemHdfs.java

## Purpose

`TestViewFileSystemHdfs` runs ViewFileSystem against a federated two-namespace HDFS cluster and extends the base ViewFS contract with HDFS-specific behavior. It validates delegation tokens, trash roots, shell `-df`, checksums, cross-filesystem rename rejection, Nfly repair behavior, lazy target initialization under UGI, internal directory permissions, and encryption-zone enclosing-root resolution.

## Important APIs, types, and functions

The test depends on `ViewFileSystemBaseTest`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `FileSystem`, `FsShell`, `DFSTestUtil`, `HdfsAdmin`, `CreateEncryptionZoneFlag.PROVISION_TRASH`, `NflyFSystem.NflyKey`, `ConfigUtil.addLinkNfly`, `ConfigUtil.addLinkFallback`, `FileChecksum`, `UserGroupInformation`, and `LambdaTestUtils`. Important methods are `setupMountPoints`, `testTrashRootsAfterEncryptionZoneDeletion`, `testDf`, `testFileChecksum`, `testRenameAccorssFilesystem`, `testNflyRepair`, `testTargetFileSystemLazyInitializationWithUgi`, and `testEnclosingRoot*`.

## Control flow, state, and persistence

`@BeforeAll` configures a JKS key provider, encryption-zone listing batch size, delegation tokens, starts two federated NameNodes, and creates per-namespace working directories. Each test mounts the first namespace through inherited links and adds `/mountOnNn2` to the second namespace. Tests then manipulate HDFS files, encryption zones, Nfly target roots, permissions, and child filesystem instantiation. Persistent state is MiniDFSCluster namespace metadata and key-provider files under the test root; cleanup deletes keys and cluster state.

## Dependencies and integration points

This file integrates ViewFS with HDFS federation, encryption zones and provisioned trash, FsShell output, file checksum passthrough, Nfly replicated filesystem routing, UGI-sensitive lazy target creation, fallback filesystem handling, and `getEnclosingRoot` semantics across mounts and encryption-zone boundaries.

## Risks and test signals

Risks include wrong delegation-token deduplication, checksum delegation bugs, accidental cross-namespace rename support, Nfly not repairing missing replicas, target filesystems initialized under the wrong user, and incorrect enclosing-root discovery for encryption zones. Test signals include exact child token counts, shell output fragments, checksum equality, expected `AccessControlException`, repaired missing files, and `NotInMountpointException`/`IllegalArgumentException` for invalid roots.
