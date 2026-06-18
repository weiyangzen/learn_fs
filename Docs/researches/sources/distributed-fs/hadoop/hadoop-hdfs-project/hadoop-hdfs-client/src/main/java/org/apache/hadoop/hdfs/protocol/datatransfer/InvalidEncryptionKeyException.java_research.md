# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/InvalidEncryptionKeyException.java

## Purpose
`InvalidEncryptionKeyException` signals that an HDFS data transfer encryption key failed verification during SASL/data transfer negotiation.

## Important APIs, Types, and Functions
It extends `IOException`, has a no-arg constructor and a string-message constructor, and defines a serial version UID.

## Control Flow
`DataTransferSaslUtil.readSaslMessage` throws it when a SASL negotiation message has status `ERROR_UNKNOWN_KEY`. `DataEncryptionKeyFactory.clearDataEncryptionKey` is intended to be called by retry paths after this exception.

## State and Persistence Behavior
Only exception message state is stored. It influences retry behavior rather than persistent metadata.

## Dependencies and Integration Points
It integrates with encrypted data transfer SASL negotiation, `DataEncryptionKeyFactory`, DFS client retry logic, and DataNode SASL server responses.

## Risks and Edge Cases
Preserving this specific exception type matters because callers may refresh encryption keys and retry. Wrapping it as generic `IOException` could break recovery. Empty messages are possible from the no-arg constructor.

## Test Signals
Encrypted transfer tests should cover invalid key responses and key-cache clearing/retry behavior.
