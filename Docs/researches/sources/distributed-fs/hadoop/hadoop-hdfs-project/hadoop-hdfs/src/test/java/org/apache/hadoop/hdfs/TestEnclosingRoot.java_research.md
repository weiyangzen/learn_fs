# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEnclosingRoot.java

## Purpose
Verifies `DistributedFileSystem.getEnclosingRoot` for ordinary paths and paths inside an encryption zone. The core contract is that `/` remains the enclosing root outside special roots, while an encryption zone root becomes the enclosing root for the zone and for non-existent descendants beneath it.

## Important APIs and Types
Uses `MiniDFSCluster`, `DistributedFileSystem`, `HdfsAdmin.createEncryptionZone`, `CreateEncryptionZoneFlag.NO_TRASH`, `JavaKeyStoreProvider`, `FileSystemTestHelper`, `DFSTestUtil.createKey`, and `EncryptionZoneManager` logging.

## Control Flow
`setup()` creates a JKS-backed key provider under the test root, enables delegation-token key usage, starts a one-DataNode cluster, installs the NameNode key provider into the DFS client, and creates `test_key`. The single test checks `/` and `/zone1` before zone creation, creates `/zone1` as an encryption zone, then checks the root path, the zone root, a non-existent file under the zone, and a non-existent nested directory/file under the zone.

## State, Persistence, Dependencies, Integration
State lives in the NameNode encryption-zone map and the JKS key provider. The test does not restart the cluster, so it focuses on live namespace resolution rather than fsimage/edit-log durability. It integrates the public DFS API with `HdfsAdmin` zone creation and the client-side key provider hook needed for JKS tests.

## Risks and Test Signals
The strongest signal is non-existent descendant handling, because callers can ask for enclosing roots before creating files. Risks include provider setup mistakes masking namespace behavior; teardown resets `EncryptionFaultInjector` to prevent leakage into other encryption tests.
