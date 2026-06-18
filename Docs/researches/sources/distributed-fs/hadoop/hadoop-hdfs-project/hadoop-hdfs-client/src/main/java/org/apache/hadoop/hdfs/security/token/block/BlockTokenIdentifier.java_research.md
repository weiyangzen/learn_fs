# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenIdentifier.java

## Purpose

`BlockTokenIdentifier.java` defines the HDFS block access token identifier. It describes who may access a block, which block pool/block ID it covers, permitted access modes, optional storage-type/storage-ID restrictions, expiry/key metadata, and an optional handshake secret. It supports both legacy Writable serialization and newer protobuf serialization for upgrade compatibility.

## Important APIs, Types, and Functions

The class extends `TokenIdentifier`, declares `KIND_NAME` as `HDFS_BLOCK_TOKEN`, and defines `AccessMode` values `READ`, `WRITE`, `COPY`, and `REPLACE`. Important methods include constructors, `getKind`, `getUser`, getters/setters for expiry/key/handshake, `equals`, `hashCode`, `toString`, `readFields`, `readFieldsLegacy`, `readFieldsProtobuf`, `write`, `writeLegacy`, `writeProtobuf`, `getBytes`, and nested `Renewer`.

## Control Flow

`readFields` caches the raw input bytes, peeks at the first byte, and chooses legacy decoding for first bytes `<= 0` or protobuf decoding otherwise. Legacy decoding reads VLong/VInt/String fields, access modes, and then attempts newer storage type, storage ID, and handshake fields inside an EOF-tolerant block so older tokens still parse. Protobuf decoding parses `BlockTokenSecretProto` and maps modes/storage types through `PBHelperClient`. `write` dispatches to protobuf or legacy based on `useProto`. Mutators invalidate the cached byte representation.

## State and Persistence Behavior

State is the token identity fields and a `cache` of serialized bytes. The cache preserves unknown protobuf bytes after reading so unchanged tokens can return original bytes for password lookup and upgrade compatibility. Mutating expiry, key ID, or handshake invalidates the cache. The object serializes to token identifier bytes that are stored in Hadoop `Token` instances and used by DataTransferProtocol authorization.

## Dependencies and Integration Points

Dependencies include Hadoop token APIs, `UserGroupInformation`, Writable utilities, `StorageType`, `BlockTokenSecretProto`, `PBHelperClient`, and IO utilities. It integrates with block token secret managers, DataNode block access checks, client block tokens in located blocks, and `PBHelperClient` token conversion.

## Risks and Edge Cases

Serialization detection depends on first-byte conventions and requires a mark-supported `DataInputStream`; passing another `DataInput` shape fails. Legacy `writeLegacy` writes storage/handshake sections only when arrays/messages are non-null/non-empty, while legacy reads tolerate EOF for older tokens. `equals` and `hashCode` do not include `useProto`, `handshakeMsg`, or cache, which is intentional for identity but important for tests. `setHandshakeMsg` does not defensively copy the input byte array.

## Test Signals

Tests should cover legacy and protobuf round trips, parsing older legacy tokens without storage/handshake fields, raw-byte cache preservation after protobuf reads, cache invalidation on mutators, access-mode conversion, user fallback to `blockPoolId:blockId`, equality/hash behavior, and invalid/non-mark-supported input streams.
