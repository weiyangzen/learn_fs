# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/TestRpcCallCache.java

Purpose: Tests duplicate-request cache behavior for ONC/RPC calls, including size validation, in-progress/completed entries, and eviction order.

Important APIs/types/functions: `RpcCallCache`, `RpcCallCache.CacheEntry`, `RpcCallCache.ClientRequest`, `checkOrAddToCache`, `callCompleted`, `iterator`, `size`, mocked `RpcResponse`, and `InetAddress`.

Control flow: constructor tests reject zero and negative sizes. Add/remove coverage inserts a client/xid, expects first lookup to create and return null, second lookup to show in-progress, then `callCompleted` to store a response. Cache functionality loops through 20 client addresses with max size 10 and validates that only the most recent 10 entries remain in iterator order.

State and persistence: in-memory cache keyed by client address and xid; entries transition from in-progress to completed with a response reference.

Dependencies/integration points: ONC/RPC duplicate suppression for idempotency/retransmit handling.

Risks: eviction ordering is observable; address resolution of synthetic IPs must be stable; cache entry state must not conflate in-progress duplicate calls with completed replay responses.

Test signals: verifies capacity bounds, insertion semantics, completed-response retention, and FIFO-style eviction of old client requests.
