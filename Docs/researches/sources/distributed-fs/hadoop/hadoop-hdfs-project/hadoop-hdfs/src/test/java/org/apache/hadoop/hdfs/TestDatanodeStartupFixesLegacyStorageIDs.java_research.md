# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeStartupFixesLegacyStorageIDs.java

Purpose: verifies that DataNode startup or layout upgrade replaces legacy storage IDs with UUID-based IDs, while preserving already-valid unique storage IDs.

Important APIs and types: `TestDFSUpgradeFromImage`, `ClusterVerifier`, `DatanodeStorage.isValidStorageId`, `StorageReport`, `MiniDFSCluster.Builder`, `GenericTestUtils.getMethodName`, and AssertJ/JUnit assertions.

Control flow: `runLayoutUpgradeTest` unpacks a fixture named after the test method, initializes data/name dirs, runs shared upgrade verification, then inspects the first DataNode storage report. It asserts the storage ID is valid and optionally equals an expected preserved ID. Three tests cover upgrade from 2.2, startup from a 2.6 layout with legacy IDs, and startup from a 2.6 layout with a valid existing ID.

State and persistence: unpacks historical NN/DN images, performs upgrade/startup with unmanaged dirs, reads block-pool storage reports, and validates/generated storage IDs.

Dependencies and integration: shares checksum-based image upgrade verification and then adds DataNode storage-ID-specific assertions against fsdataset reports.

Risks: fixture names are tied to test method names; storage report ordering assumes a single report; generated UUID values are validated only structurally unless an expected ID is supplied.

Test signals: successful upgrade verification, exactly one storage report, valid `DS-...` storage ID format, and exact preservation of the known valid storage ID in the preservation case.
