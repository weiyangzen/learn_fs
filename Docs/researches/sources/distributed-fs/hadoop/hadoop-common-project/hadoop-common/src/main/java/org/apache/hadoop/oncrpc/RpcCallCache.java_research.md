# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcCallCache.java

Purpose: duplicate suppression cache for non-idempotent RPC calls, keyed by client address and xid.

Important APIs/types/functions: `CacheEntry`, `ClientRequest`, constructor with max entries, `checkOrAddToCache`, `callCompleted`, `size`, `iterator`, and `getProgram`.

Control flow: `checkOrAddToCache` synchronizes on the map, returns an existing entry or inserts a new in-progress entry and returns null. `callCompleted` locates the entry and stores the response. The backing `LinkedHashMap` evicts the eldest entry when size exceeds the configured maximum.

State and persistence: in-memory bounded map only; cache entries transition from in-progress (`response == null`) to completed (`response != null`).

Dependencies and integration: used by RPC services that need retransmission handling for non-idempotent procedures. Stores `RpcResponse` for replay.

Risks: `callCompleted` assumes a prior cache entry and will null-dereference if called without `checkOrAddToCache`. `size` and `iterator` are not synchronized, so test/introspection callers can observe concurrent modification. Eviction is insertion-order, not access-order.

Test signals: `TestRpcCallCache` covers duplicate detection, completion, eviction, equality, and invalid sizes.
