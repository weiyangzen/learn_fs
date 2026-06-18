# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataTransferEncryptionKey.java

Purpose: small unit test for DataNode data-transfer retry behavior after `InvalidEncryptionKeyException`, specifically that the cached data encryption key is cleared only on the first retry.

Important APIs and types: private static `DataNode.prepareRetryAfterInvalidEncryptionKey`, accessed reflectively, `DataEncryptionKeyFactory`, `DataEncryptionKey`, and an inner `CountingKeyFactory` that records `clearDataEncryptionKey` calls.

Control flow: `testClearEncryptionKeyOnRetry` invokes the private method with retry count 1 and verifies it returns true and clears exactly once. It then invokes retry count 2 and verifies it returns false without additional clears. The helper uses `DataNode.class.getDeclaredMethod`, `setAccessible(true)`, and reflective invocation.

State and persistence behavior: all state is in the in-memory `clearCount` field of `CountingKeyFactory`; no cluster or filesystem is involved. Integration point is SASL/encrypted data transfer retry logic in DataNode. Risks include brittle reflection if the private method signature changes, method accessibility under stricter Java/module policies, and limited behavior coverage beyond retry counts 1 and 2. Test signals are boolean retry decisions and `clearCount`.
