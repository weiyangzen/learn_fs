# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenSecretManager.java

## Purpose
`BlockTokenSecretManager` manages HDFS block access token secrets. In master mode, typically in a NameNode, it generates and rotates block keys and exports them. In worker mode, typically in DataNodes and clients such as the balancer, it imports exported keys and verifies or generates tokens with the current key.

## Important APIs and types
Constructors distinguish worker mode from master mode and support HA NameNode key ID ranges. Key lifecycle methods are `generateKeys`, `exportKeys`, `addKeys`, `updateKeys`, and `removeExpiredKeys`. Token APIs include `generateToken`, `createPassword`, `retrievePassword`, `checkAccess` overloads, and `isTokenExpired`. Data encryption APIs are `generateDataEncryptionKey` and `retrieveDataEncryptionKey`.

## Control flow
Master construction computes a unique serial-number range from NameNode index and number of NameNodes, seeds a serial number, and generates current/next keys. `updateKeys` retires the old current key with a shorter final expiry, promotes `nextKey`, and creates a new future key. Worker `addKeys` removes expired keys, optionally updates the current key, and merges received key material. Token generation creates a `BlockTokenIdentifier` for user, block pool, block ID, access modes, storage types, and storage IDs; optionally wraps the established RPC QOP in the identifier. Verification deserializes token identifiers when needed, checks user/block/pool/expiry/mode/storage constraints, and recomputes HMAC-like passwords with the referenced `BlockKey`.

## State and persistence
State is in memory: `currentKey`, `nextKey`, `allKeys`, key update interval, token lifetime, serial number range, block pool ID, encryption algorithm, proto-token flag, QOP wrapping flag, random nonce generator, and testable `Timer`. Persistent transfer of key material occurs through `ExportedBlockKeys`; this class itself does not write storage.

## Dependencies and integration points
It depends on Hadoop `SecretManager`, `Token`, `BlockTokenIdentifier`, `ExtendedBlock`, `DataEncryptionKey`, storage types, server-side QOP, `UserGroupInformation`, `Timer`, and crypto primitives inherited from `SecretManager`. It is central to DataTransferProtocol authorization and encryption.

## Risks and edge cases
Incorrect HA `nnIndex` or `numNNs` can produce overlapping key ID ranges if configuration is wrong. Worker mode silently ignores `addKeys` when called on a master or with null exported keys. Missing keys cause token verification and data encryption key reconstruction failures, so clock skew and key distribution delays affect live IO. The static storage constraint checker allows empty candidate lists to mean unrestricted token side, but rejects empty requested lists as a likely configuration error.

## Test signals
Tests should cover master/worker constructor behavior, serial range partitioning, key rotation timing, export/import round trips, expired key removal, token creation and password retrieval, user/block/pool/mode/storage mismatch failures, QOP wrapping, data encryption key reconstruction, and timer-driven expiry behavior.
