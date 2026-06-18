# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/KeyManager.java

## Purpose

`KeyManager` provides the balancer with block access tokens and optional data-transfer encryption keys. It mirrors NameNode-exported block keys into a local `BlockTokenSecretManager`, refreshes them periodically, and supplies tokens for `REPLACE` and `COPY` DataNode operations.

## Important APIs, Types, and Functions

The constructor fetches `ExportedBlockKeys` from `NamenodeProtocol`, detects whether block tokens are enabled, initializes `BlockTokenSecretManager`, and creates a `BlockKeyUpdater` daemon at one quarter of the NameNode key update interval. `startBlockKeyUpdater()` starts refresh. `getAccessToken()` returns a dummy token when block tokens are disabled or generates a token with `REPLACE` and `COPY` access modes for a specific `ExtendedBlock`, storage types, and storage IDs. `newDataEncryptionKey()` implements `DataEncryptionKeyFactory`, caching an encryption key until expiry. `clearDataEncryptionKey()`, `updateBlockKeys()`, and `close()` manage key refresh and shutdown.

## Control Flow

At connector startup, `NameNodeConnector` creates a `KeyManager` after reading server defaults for encrypt-data-transfer. Factory methods then call `startBlockKeyUpdater()`. During a move, `Dispatcher.PendingMove.dispatch()` asks for an access token and passes the key manager into SASL negotiation. If DataNode negotiation throws `InvalidEncryptionKeyException`, the dispatcher calls `updateBlockKeys()` and `clearDataEncryptionKey()` once before retrying.

The updater daemon loops while `shouldRun`, fetching keys from the NameNode and adding them to the local secret manager. `newDataEncryptionKey()` synchronizes around the cached key so concurrent move threads share a still-valid key and only regenerate when absent or expired.

## State and Persistence Behavior

All state is process-local: NameNode proxy, booleans for token/encryption mode, `shouldRun`, secret manager, updater daemon, cached `DataEncryptionKey`, and testable `Timer`. It does not persist keys; they are fetched from the NameNode and kept in memory. `close()` flips `shouldRun` and interrupts the daemon.

## Dependencies and Integration Points

It depends on `NamenodeProtocol.getBlockKeys()`, `ExportedBlockKeys`, `BlockTokenSecretManager`, `BlockTokenIdentifier`, `DataEncryptionKeyFactory`, HDFS encryption configuration keys, and Hadoop `Daemon`/`Timer`. It integrates with `NameNodeConnector` lifecycle and `SaslDataTransferClient` during balancer moves.

## Risks and Edge Cases

If block tokens are enabled but the updater has been closed, `getAccessToken()` throws. The updater logs and continues after `IOException`, but unexpected `Throwable` disables future token generation by setting `shouldRun` false. `updateInterval / 4` assumes a positive NameNode interval. The cached encryption key relies on token lifetime/key lifetime invariants in `BlockTokenSecretManager`; stale keys surface as transfer negotiation failures and only one retry is attempted by `Dispatcher`.

## Test Signals

Tests should cover token-disabled dummy-token behavior, token-enabled access modes, updater startup/shutdown, failure after close, encryption key caching and expiry using a controllable timer, clearing cached keys, explicit block-key update, and dispatcher retry behavior after invalid encryption keys.
