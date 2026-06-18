# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirEncryptionZoneOp.java

## Purpose
`TestFSDirEncryptionZoneOp` verifies retry behavior in the encrypted data encryption key cache warm-up path used by encryption-zone operations.

## Important APIs, Types, And Functions
The test initializes NameNode metrics, mocks `KeyProviderCryptoExtension`, and constructs `FSDirEncryptionZoneOp.EDEKCacheLoader` with an array of key names, an initial delay, retry interval, and `maxRetries`. It verifies calls to `warmUpEncryptedKeys`.

## Control Flow
The mocked key provider throws `IOException` twice and would succeed on a third call. The loader is configured with `maxRetries = 2`, then run synchronously. The verification expects exactly two warm-up attempts, proving the loader stops at the configured retry limit rather than continuing to the later success answer.

## State And Persistence Behavior
The loader does not persist namespace state in this test. Its relevant state is retry count and scheduling delays. The test protects operational behavior around external KMS failures: warm-up should retry transient failures but remain bounded.

## Dependencies And Integration Points
This test integrates encryption-zone namespace code with Hadoop crypto key-provider APIs and NameNode metrics initialization. It uses a direct unit path rather than creating real encryption zones or a KMS.

## Risks And Test Signals
Risks include unbounded retry loops, too few warm-up attempts, or accidental dependency on metrics being initialized elsewhere. The test signal is the Mockito verification that `warmUpEncryptedKeys` is called exactly `maxRetries` times.
