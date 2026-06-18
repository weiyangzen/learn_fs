
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestKeyManager.java

## Purpose
`TestKeyManager` validates HDFS balancer-side block-token key management, especially the generation, caching, expiry, clearing, and refresh behavior of `KeyManager` data encryption keys. The test class is focused on security-sensitive data-transfer encryption paths where the balancer asks the NameNode for exported block keys through `NamenodeProtocol`.

## Important APIs, Types, and Functions
The central production types are `KeyManager`, `BlockTokenSecretManager`, `DataEncryptionKey`, `ExportedBlockKeys`, and `NamenodeProtocol`. The tests use `HdfsConfiguration` with `DFS_ENCRYPT_DATA_TRANSFER_KEY` and `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY` enabled. `FakeTimer` and `Whitebox.setInternalState` replace internal timers in both `KeyManager` and its `BlockTokenSecretManager` so expiry behavior is deterministic. `createNamenode` builds a dynamic proxy for `NamenodeProtocol`, supporting only `getBlockKeys` and optionally counting calls.

## Control Flow and State
`testNewDataEncryptionKey` exports keys from a `BlockTokenSecretManager`, constructs a `KeyManager`, gets a DEK, advances fake time beyond the key interval, then checks that `newDataEncryptionKey` returns a new non-expired key. `testClearDataEncryptionKey` proves the unexpired DEK is cached by identity, then calls `clearDataEncryptionKey` and verifies a replacement object is generated. `testUpdateBlockKeysThenClearDataEncryptionKey` combines `updateBlockKeys` with cache clearing and verifies the NameNode key fetch count reaches two.

## Dependencies and Integration Points
This file integrates balancer key handling with HDFS configuration keys, block-token secret manager exports, NameNode protocol fetches, and test-only reflection utilities. It does not start a MiniDFSCluster; it isolates the protocol dependency with Mockito or a dynamic proxy.

## Risks and Test Signals
The main risks are stale encryption-key reuse, expired DEK issuance after clock advancement, and accidental loss of NameNode key refresh behavior when the cache is cleared. Strong signals are identity assertions (`assertSame`/`assertNotSame`), fake-time expiry assertions, and proxy call counting. Reflection into private timers is brittle but appropriate for deterministic expiry testing.
