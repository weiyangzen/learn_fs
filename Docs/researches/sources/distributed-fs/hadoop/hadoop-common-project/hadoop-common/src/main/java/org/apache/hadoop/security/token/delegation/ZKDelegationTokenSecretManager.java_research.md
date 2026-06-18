<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/ZKDelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/ZKDelegationTokenSecretManager.java

Source read size: 881 lines, 33114 bytes.

## Purpose
ZooKeeper-backed delegation token secret manager for HA services. It stores master keys and token records in znodes, uses Curator shared counters for id allocation, and optionally watches token/key znode changes into local caches.

## Important APIs, Types, and Functions
Key APIs are `createCuratorClient()`, `startThreads()`, `stopThreads()`, `incrementDelegationTokenSeqNum()`, `incrementCurrentKeyId()`, `getDelegationKey()`, `getTokenInfo()`, `storeDelegationKey()`, `updateDelegationKey()`, `storeToken()`, `updateToken()`, `removeStoredToken()`, `cancelToken()`, and `isTokenWatcherEnabled()`. Static config constants cover ZK connection/auth/SSL, znode path, retry/session timeouts, sequence batch size, and token watcher behavior.

## Control Flow, State, and Persistence Behavior
Construction either uses a thread-local external Curator client or creates one. `startThreads()` starts Curator, shared counters, persistent roots, key cache, optional token cache, loads cache contents, then starts base key-rolling/removal threads. Token sequence numbers are reserved in batches from `SharedCount`; key ids increment one at a time. Key/token znodes are named with `DK_` and `DT_` prefixes and contain writable-serialized data. Reads check local maps first, then ZK. Deletion uses guaranteed deletes and can double-check renew date to avoid removing a token renewed by a peer.

## Dependencies and Integration Points
Depends on Apache Curator caches/shared counters, Hadoop ZK client/auth helpers, Kerberos/SSL configuration, `DelegationTokenManager` timing keys, and the base secret manager. Web filters can inject the same Curator used by `ZKSignerSecretProvider`.

## Risks and Test Signals
Risks include watcher lag or missed events, znode ACL mistakes when namespace parents are implicit, sequence gaps from batching, infinite retry loops in shared-count updates, runtime exceptions on ZK write failures, and local owner stats needing sync after cache reload. Test external and owned Curator modes, SSL/Kerberos config, cache load with corrupt nodes, watcher create/update/delete events, sequence batch boundaries, key lookup fallback, token renewal/delete races, watcher disabled mode, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/ZKDelegationTokenSecretManager.java -->
