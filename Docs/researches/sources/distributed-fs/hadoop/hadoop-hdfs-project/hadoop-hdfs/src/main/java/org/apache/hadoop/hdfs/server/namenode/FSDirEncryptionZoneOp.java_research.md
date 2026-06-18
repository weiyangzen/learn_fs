# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirEncryptionZoneOp.java

## Purpose
`FSDirEncryptionZoneOp` implements encryption-zone management and per-file encryption metadata handling. It creates/list zones, resolves zone information, maintains re-encryption progress XAttrs, saves file EDEKs, warms KMS EDEK caches, and coordinates file creation with key generation outside Namenode locks.

## Important APIs, Types, And Functions
- Zone APIs: `ensureKeyIsInitialized`, `createEncryptionZone`, `getEZForPath`, `listEncryptionZones`, `listReencryptionStatus`, `getCurrentKeyVersion`, and `getKeyNameForZone`.
- Re-encryption APIs: `reencryptEncryptionZone`, `cancelReencryptEncryptionZone`, `updateReencryptionSubmitted`, `updateReencryptionProgress`, `updateReencryptionFinish`, and `generateNewXAttrForReencryptionFinish`.
- File encryption APIs: `setFileEncryptionInfo`, `getFileEncryptionInfo`, `isInAnEZ`, `getEncryptionKeyInfo`, and `saveFileXAttrsForBatch`.
- Helper types include `EncryptionZone`, `ZoneReencryptionStatus`, `FileEncryptionInfo`, `KeyProviderCryptoExtension`, `EncryptedKeyVersion`, protobuf zone/file encryption records, and `EncryptionKeyInfo`.

## Control Flow
Zone creation converts cipher/protocol information, resolves the target under the write lock, asks `EncryptionZoneManager` to create the zone XAttr, then logs it as a set-XAttrs edit. File creation first checks whether the path is in a zone, chooses a supported crypto protocol, releases the FS write lock, generates an EDEK as the login user through the configured key provider, then reacquires the lock and requires the caller to re-resolve/revalidate before use. Re-encryption status updates parse the zone XAttr protobuf, build a replacement protobuf with submitted/progress/finish fields, and apply it via `FSDirXAttrOp.unprotectedSetXAttrs`. File encryption info reads the per-file XAttr plus zone cipher/protocol/key name and returns a consolidated `FileEncryptionInfo`.

## State And Persistence Behavior
Encryption-zone and re-encryption state is persisted as crypto XAttrs and mirrored in `EncryptionZoneManager` in-memory maps. Per-file encryption info is stored as `CRYPTO_XATTR_FILE_ENCRYPTION_INFO`. Re-encryption batch saves emit `logSetXAttrs` for updated file XAttrs. Metrics record EDEK generation and warm-up latency. Some methods intentionally require callers to log/sync after XAttr mutation.

## Dependencies And Integration Points
The file integrates with KMS/key provider APIs, `SecurityUtil.doAsLoginUser`, `EncryptionZoneManager`, `ReencryptionUpdater`, `FSDirXAttrOp`, `PBHelperClient`, `FSNamesystem` lock modes, `NameNode` metrics/logging, and file creation in `FSDirWriteFileOp`.

## Risks And Edge Cases
Key generation must not run under FS read/write locks. Zone changes between lock release and reacquire are handled by retry exceptions and key-name revalidation. Raw paths intentionally suppress encryption info. Missing or unparsable XAttrs degrade to warnings or IOExceptions depending on context. Re-encryption XAttr updates must preserve existing zone cipher/protocol/key fields while changing only re-encryption state.

## Test Signals
Tests should cover missing provider/key errors, EDEK generation outside locks, zone/key mismatch retry during file creation, raw path returning no encryption info, malformed per-file/zone XAttr parsing, re-encryption submitted/progress/finish XAttr replacements, list batching, cache warm-up retry behavior, and edit-log replay rebuilding EZ state from XAttrs.
