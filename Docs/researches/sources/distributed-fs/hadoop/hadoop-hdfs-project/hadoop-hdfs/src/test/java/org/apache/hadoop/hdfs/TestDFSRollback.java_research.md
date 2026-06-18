# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRollback.java

Purpose: This upgrade test validates NameNode, DataNode, and block-pool rollback success and failure behavior across valid storage snapshots, missing snapshots, incompatible layout versions, newer federation state times, missing edits/images, and corrupt VERSION files.

Important APIs/types/functions: `UpgradeUtilities`, `NameNode.doRollback`, `MiniDFSCluster.Builder`, `StartupOption.ROLLBACK/UPGRADE`, `StorageInfo`, `DataNodeLayoutVersion`, `FSImageTestUtil`, `BlockPoolSliceStorage` via utility-created dirs, and helper methods `checkResult`, `startNameNodeShouldFail`, `startBlockPoolShouldFail`, and `deleteMatchingFiles`.

Control flow: For one and two storage dirs, the test repeatedly constructs synthetic `current` and `previous` states. It runs normal NameNode rollback, normal DataNode rollback, and block-pool rollback with a deliberately newer current layout. It then checks failure cases: no previous dir, future layout version in previous, newer fsscTime, missing edits, missing image, corrupt VERSION layoutVersion, and too-old layout version. Expected failures are validated by exception message substrings or dead block-pool service state.

State and persistence behavior: The file directly manipulates on-disk NameNode/DataNode storage directories, VERSION files, fsimage/edits files, namespace IDs, cluster IDs, block-pool IDs, and layout/fsscTime metadata. Successful rollback must promote `previous` to `current`, remove `previous`, and preserve parallel-identical/current checksummed contents.

Dependencies and integration points: It depends on the upgrade utility fixture, NameNode rollback code, DataNode block-pool service startup, layout-version compatibility checks, and MiniDFSCluster unmanaged-dir startup.

Risks and test signals: Signals include checksum comparisons, `previous` directory removal, NameNode failure message substrings, and `isBPServiceAlive` false for bad block-pool rollback. Risks include brittle failure-message matching, many storage-state mutations in one long test, and assumptions about utility master checksums.
