# sources/distributed-fs/beegfs/common/source/common/nodes/NodeConnPool.cpp

## Purpose
Implements per-node stream connection pooling for TCP and RDMA internode communication. It caps concurrent connections, reuses idle pooled sockets, chooses NIC routes, authenticates channels, and invalidates stale or failed sockets.

## Important APIs, Types, And Functions
Key methods are the constructor/destructor, `setLocalNicList()`, `loadIpSourceMap()`, `acquireStreamSocketEx()`, `releaseStreamSocket()`, `invalidateStreamSocket()`, `invalidateSpecificStreamSocket()`, `invalidateAllAvailableStreams()`, `disconnectAndResetIdleStreams()`, `updateInterfaces()`, `getFirstPeerName()`, socket option helpers, `authenticateChannel()`, and `makeChannelIndirect()`.

## Control Flow
`acquireStreamSocketEx()` waits on `changeCond` when all connections are busy and waiting is allowed. If an available pooled socket exists, it marks it unavailable and returns it. Otherwise it increments `establishedConns`, releases the mutex, iterates known NICs, filters by net/tcp-only settings, creates RDMA or TCP sockets, binds an optional source IP, connects, applies options, sends auth/directness control messages, and then re-locks to append the socket or roll back the count. Releases either mark a socket available and signal waiters or invalidate expired/close-on-release sockets. Invalidation collects available sockets under lock, closes them outside the lock, and decrements stats through `invalidateSpecificStreamSocket()`.

## State, Persistence, And Dependencies
State is in-memory: NIC lists, source-IP map, `connList`, available/established counters, max connection limit, fallback expiration, direct-channel flag, stats, error-log suppression state, mutex, and condition variable. It depends on `AbstractApp`/common config, `PThread`, net filters, `RoutingTable`, `StandardSocket`, `RDMASocket`, `PooledSocket`, `MessagingTk`, and control messages.

## Integration Points
Each `Node` owns a pool. `NodeStoreServers` and `NodeStoreClients` set channel directness and local NIC capabilities. Messaging paths acquire sockets for request/response traffic. Internode sync uses `disconnectAndResetIdleStreams()` for idle cleanup.

## Risks
The pool relies on correct accounting of `establishedConns` versus `connList.size()`, especially across exceptions. `invalidateSpecificStreamSocket()` searches with a loop that dereferences the iterator before checking `end()`; empty or corrupted lists would be dangerous. Route restriction needs `ipSrcMap` freshness. Filters can silently skip all NICs. Authentication is one-way send here; failures surface as socket errors later. Fallback sockets expire only after release.

## Test Signals
Exercise TCP, RDMA, mixed NIC ordering, filter rejection, source-interface restriction, max-connection blocking and nonblocking acquire, failed-all-routes logging suppression, close-on-release after interface changes, idle disconnect, auth hash enabled, indirect channel mode, destructor cleanup, and concurrent acquire/release stress.
