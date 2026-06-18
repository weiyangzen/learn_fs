# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/ZKDelegationTokenSecretManagerImpl.java

## Purpose
`ZKDelegationTokenSecretManagerImpl` is the ZooKeeper-backed router delegation token secret manager, with additional local token-cache synchronization for configurations where token watchers are disabled.

## Important APIs, Types, And Functions
It extends `ZKDelegationTokenSecretManager<AbstractDelegationTokenIdentifier>`. Important members include sync interval config, a single-thread scheduler, `localTokenCache`, `TOKEN_PATH`, and `checkAgainstZkBeforeDeletion`. Overrides include `startThreads`, `stopThreads`, `createIdentifier`, `cancelToken`, `removeStoredToken`, and `addOrUpdateToken`.

## Control Flow
Construction calls `startThreads` and logs startup. `startThreads` calls the superclass and, if token watchers are disabled, ensures the token root znode exists, rebuilds the local cache immediately, and schedules periodic cache rebuilds. Rebuild reads token child names through the raw ZooKeeper client, fetches token data via Curator, processes each token into `currentTokens`, and removes local tokens no longer present in ZooKeeper on non-initial runs. `cancelToken` temporarily disables extra ZK deletion checks because it is an explicit cancel path.

## State, Persistence, And Dependencies
Durable state lives in ZooKeeper znodes under the token root. Process-local state includes superclass token maps, `localTokenCache`, the scheduler, and a thread-local deletion-check flag. Dependencies include Hadoop ZK delegation token manager, Curator/ZooKeeper APIs, and Hadoop `Time`.

## Integration Points
Selected by router security configuration through `FederationUtil.newSecretManager`. It feeds `RouterSecurityManager` token operations and synchronizes token state among multiple routers.

## Risks
Constructor logs `startThreads` failures instead of failing construction, which can leave an unusable manager. `currentTokens` is mutated while iterating key sets during rebuild; concurrency depends on superclass map behavior. Scheduler exceptions are swallowed, so cache sync can silently stall. Raw ZooKeeper child listing avoids Curator sorting for scale but bypasses some Curator conveniences.

## Test Signals
Tests should cover watcher-enabled and watcher-disabled startup, root znode creation, initial and periodic cache rebuild, removal of deleted tokens, cancellation deletion-check behavior, scheduler shutdown, and failure modes when ZooKeeper is unavailable.
