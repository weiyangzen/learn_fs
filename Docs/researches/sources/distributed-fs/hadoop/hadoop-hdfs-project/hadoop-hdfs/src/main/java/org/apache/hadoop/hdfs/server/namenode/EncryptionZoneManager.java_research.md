# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EncryptionZoneManager.java

## Purpose
`EncryptionZoneManager` manages HDFS encryption-zone metadata and re-encryption lifecycle state. It maps encryption-zone root inode IDs to cryptographic suite/version/key metadata, validates moves across zones, creates zone xattrs, lists zones/statuses, and coordinates background `ReencryptionHandler` threads.

## Important APIs and Types
`EncryptionZoneInt` is the internal zone record. Core state includes `TreeMap<Long, EncryptionZoneInt> encryptionZones`, `FSDirectory dir`, list response limits, optional re-encryption executor/handler, and `ReencryptionStatus`. Important APIs cover testing pauses, constructor setup, thread start/stop, zone add/remove, `isInAnEZ`, `getKeyName`, `getEZINodeForPath`, `checkMoveValidity`, `createEncryptionZone`, `listEncryptionZones`, `reencryptEncryptionZone`, `cancelReencryptEncryptionZone`, `listReencryptionStatus`, `isEncryptionZoneRoot`, `checkEncryptionZoneRoot`, `getNumEncryptionZones`, and `getKeyNames`.

## Control Flow
Zone creation validates that the target exists, is a directory, is not already a zone, and is empty, then writes the crypto xattr via `FSDirXAttrOp`; xattr handling calls back to add the zone so fsimage/edit-log loading shares the same path. Zone lookup walks path components upward, using the live map for current paths or xattrs for snapshots. Move validation rejects moves into/out of zones or between different zones and also blocks moves while the relevant zone is under re-encryption. Listing uses inode ID cursors and re-resolves full paths to filter snapshot-only zones.

## State and Persistence
The authoritative durable metadata is the encryption xattr on the zone inode and re-encryption xattrs/status persisted by related FSDir operations. The `encryptionZones` map and `ReencryptionStatus` are in-memory indexes reconstructed from namespace metadata.

## Dependencies and Integration
It integrates with `FSDirectory`, `FSNamesystem` locks, `KeyProviderCryptoExtension`, `ReencryptionHandler`, `ReencryptionStatus`, xattr helpers, protobuf crypto metadata, snapshots, and permission/path resolution.

## Risks and Test Signals
The class comment warns not to take the `FSDirectory` lock while holding the manager lock; actual methods primarily rely on FSDirectory lock assertions. `removeEncryptionZone` returns early if the removed zone lacks running re-encryption status, which makes handler cleanup conditional. Listing can underfill a page after filtering snapshot-only zones while still setting `hasMore` from the unfiltered tail size. Tests should cover snapshot zone lookup, rename restrictions, non-empty directory rejection, missing key provider for re-encryption, re-encryption cancellation, list pagination with deleted/snapshotted zones, and thread start/stop under locks.
