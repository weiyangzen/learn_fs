# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestDispatcherEncryptionKey.java

## Purpose
`TestDispatcherEncryptionKey` verifies dispatcher retry handling after `InvalidEncryptionKeyException`. The expected behavior is to update block keys and clear the cached data encryption key only on the first retry.

## Important APIs, Types, and Functions
The file tests private `Dispatcher.prepareRetryAfterInvalidEncryptionKey` through reflection. It defines `CountingKeyManager`, a `KeyManager` subclass that counts `updateBlockKeys` and `clearDataEncryptionKey` calls. It also builds a dynamic `NamenodeProtocol` proxy returning `ExportedBlockKeys.DUMMY_KEYS` for `getBlockKeys`.

## Control Flow
`testClearEncryptionKeyOnRetry` creates a `CountingKeyManager`, invokes the private dispatcher method with retry count 1, expects `true`, and asserts both counters incremented once. It invokes the method with retry count 2, expects `false`, and asserts counters remain unchanged. `prepareRetryAfterInvalidEncryptionKey` performs reflective lookup and invocation of the private dispatcher method.

## State and Persistence Behavior
State is in-memory only: counter fields on `CountingKeyManager` and a lightweight proxy NamenodeProtocol. No cluster or filesystem state is created.

## Dependencies and Integration Points
Integration points include dispatcher encryption-key retry policy, `KeyManager` block-key refresh and data-encryption-key cache clearing, and NamenodeProtocol block-key retrieval. Reflection makes this a direct unit test of private retry logic rather than a full data-transfer integration test.

## Risks and Test Signals
Risks include brittleness if the private method name/signature changes and limited coverage of actual `InvalidEncryptionKeyException` propagation. Signals are exact boolean return values and counter assertions proving first retry refreshes/clears once while later retry does not repeat the action.
