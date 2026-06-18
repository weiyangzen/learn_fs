# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RetryCache.java

## Purpose
`RetryCache` deduplicates retried non-idempotent RPC requests on the server by client UUID and call id, allowing successful prior responses or payloads to be reused.

## Important APIs, Types, and Functions
`CacheEntry` tracks UUID, call id, expiration, and state (`INPROGRESS`, `SUCCESS`, `FAILED`). `CacheEntryWithPayload` stores a response payload. Public/static APIs include `waitForCompletion`, `setState`, `addCacheEntry`, `addCacheEntryWithPayload`, `clear`, metric accessors, and explicit `lock`/`unlock`.

## Control Flow
`waitForCompletion` skips non-RPC, invalid call ids, and dummy client ids. Otherwise it locks the cache, inserts a new in-progress entry or finds an existing one. If existing, callers wait until completion; success returns the previous entry, while failure resets state to in-progress so the caller retries work. Completion notifies waiters.

## State and Persistence Behavior
State is a `LightWeightCache` with expiration, lock, cache name, and metrics. It is in-memory but can be repopulated from edit logs through `addCacheEntry*`, treating loaded entries as successful.

## Dependencies and Integration Points
It depends on `ClientId`, `Server.isRpcInvocation`, `RpcConstants`, lightweight Hadoop cache collections, and `RetryCacheMetrics`. HDFS NameNode operations use it for at-most-once semantics. `TestRetryCache` and `TestRetryCacheMetrics` are direct signals.

## Risks and Test Signals
Risks include UUID length validation, wait interruption handling that continues waiting, payload mutation races, expiration of still-needed results, and forgetting `setState` after work. Tests should cover concurrent retries, failed first attempts, payload reuse, skip conditions, edit-log reload, expiration, and metrics.
