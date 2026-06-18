# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEncryptionZoneManager.java

## Purpose
`TestEncryptionZoneManager` validates `EncryptionZoneManager.listEncryptionZones` when some encryption-zone inode IDs no longer resolve to valid namespace paths. The tests cover root zones, valid child zones, orphaned zones, and zones under invalid parent chains.

## Important APIs, Types, And Functions
The file uses `EncryptionZoneManager`, mocked `FSDirectory` and `INodesInPath`, `INodeDirectory`, `BatchedListEntries<EncryptionZone>`, `CipherSuite.AES_CTR_NOPADDING`, `CryptoProtocolVersion.ENCRYPTION_ZONES`, and `FSDirectory.DirOp.READ_LINK`. Setup constructs root, first, and second directory inodes and mocks `getInode` and `getINodesInPath` lookups.

## Control Flow
Each test creates a manager and adds encryption zones by inode ID. Validity is controlled by setting inode parent pointers and configuring path resolution mocks. `testListEncryptionZonesOneValidOnly` leaves one zone without a parent and expects only `/first`. `testListEncryptionZonesTwoValids` sets both parents and expects both zones. `testListEncryptionZonesForRoot` validates the special root path. `testListEncryptionZonesSubDirInvalid` adds a zone under a child whose parent chain is invalid and expects it to be skipped.

## State And Persistence Behavior
The manager stores encryption-zone entries keyed by inode ID. The tests verify that listing does not blindly persist or expose stale IDs: it resolves the inode to a path, validates the parent chain through `FSDirectory`, and returns only zones that correspond to a current, reachable namespace path. No edit-log or fsimage persistence is exercised directly.

## Dependencies And Integration Points
This is a mock-heavy unit test for NameNode encryption-zone listing. It integrates with inode parent relationships and `FSDirectory` path resolution, which are the boundaries where deleted or moved directories can make zone metadata stale.

## Risks And Test Signals
Risks include leaking stale encryption-zone entries to clients, throwing on orphaned inodes, or mishandling the root zone. Test signals are returned batch sizes, stable ordering by zone ID, and expected zone paths and IDs.
