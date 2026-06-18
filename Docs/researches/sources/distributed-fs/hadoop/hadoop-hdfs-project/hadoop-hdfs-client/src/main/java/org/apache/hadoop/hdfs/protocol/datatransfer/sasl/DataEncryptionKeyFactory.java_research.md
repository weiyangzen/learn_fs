# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/DataEncryptionKeyFactory.java

## Purpose
`DataEncryptionKeyFactory` abstracts creation and cache invalidation of HDFS data transfer encryption keys for SASL encrypted handshakes.

## Important APIs, Types, and Functions
`newDataEncryptionKey` returns a new `DataEncryptionKey` or null when encryption is not enabled, depending on the implementation. `clearDataEncryptionKey` is a default no-op hook called after `InvalidEncryptionKeyException` so implementations can force refresh on retry.

## Control Flow
`SaslDataTransferClient` asks the factory for a key when a channel is not fully trusted. If a key is returned, it chooses the specialized encrypted SASL path; otherwise it may use general SASL or skip according to security configuration.

## State and Persistence Behavior
The interface has no state. Implementations may cache keys and use `clearDataEncryptionKey` to invalidate them.

## Dependencies and Integration Points
It depends on `DataEncryptionKey` and `IOException`. It integrates with DFS client encryption setup, DataNode-to-DataNode transfers, and retry handling for invalid encryption keys.

## Risks and Edge Cases
Implementations must distinguish "encryption disabled" from "failed to fetch key" correctly. Failure to clear a bad cached key can cause repeated negotiation failures. Returning keys on trusted channels can impose unnecessary encryption.

## Test Signals
Encrypted transfer tests should verify key creation, invalid-key retry, and cache clearing behavior. Mock factories are useful for asserting when the client requests a key.
