# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/DataEncryptionKey.java

## Purpose

`DataEncryptionKey.java` is a small immutable value holder for the key material needed to encrypt HDFS DataTransferProtocol traffic.

## Important APIs, Types, and Functions

The class exposes final fields `keyId`, `blockPoolId`, `nonce`, `encryptionKey`, `expiryDate`, and `encryptionAlgorithm`. It has one constructor and a `toString()` that reports key ID, block pool ID, nonce length, and encryption-key length.

## Control Flow

There is no behavioral flow beyond construction and string formatting. Callers construct it from key manager/protobuf responses and pass it to transfer/encryption code.

## State and Persistence Behavior

Instances are immutable by field assignment, but byte arrays are not defensively copied, so callers retaining references can mutate `nonce` or `encryptionKey`. The object itself has no persistence; it is serialized by `PBHelperClient` when needed.

## Dependencies and Integration Points

The only direct dependency is `InterfaceAudience`. It integrates with NameNode key generation responses, `ClientNamenodeProtocolTranslatorPB.getDataEncryptionKey`, `PBHelperClient` conversions, and DataNode/client data-transfer encryption setup.

## Risks and Edge Cases

The constructor accepts null arrays and strings, but `toString()` dereferences `nonce.length` and `encryptionKey.length`, so partially populated instances can throw. Lack of defensive copies is important because the fields contain secret material.

## Test Signals

Tests should cover protobuf round trips, null algorithm preservation, expected `toString()` shape, expiry propagation, and defensive handling by callers that receive mutable key arrays.
