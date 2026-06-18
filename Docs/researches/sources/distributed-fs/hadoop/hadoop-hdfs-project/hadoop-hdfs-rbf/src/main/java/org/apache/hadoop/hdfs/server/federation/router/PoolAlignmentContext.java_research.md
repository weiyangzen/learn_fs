# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/PoolAlignmentContext.java

## Purpose
`PoolAlignmentContext` implements client-side RPC state-id alignment for a single router connection pool associated with a namespace and user. It propagates client-observed state IDs to NameNode requests while sharing NameNode-observed state globally through `RouterStateIdContext`.

## Important APIs, Types, And Functions
- Constructor receives a `RouterStateIdContext` and namespace ID, obtains the shared namespace `LongAccumulator`, and creates a pool-local accumulator.
- `receiveResponseState` updates the shared global state from NameNode responses and resets both accumulators when a zero state ID indicates state context is disabled.
- `updateRequestState` writes the pool-local state ID into outgoing RPC request headers.
- `advanceClientStateId` advances the pool-local value with a client-observed state ID.
- `getLastSeenStateId` exposes the shared namespace state.

## Control Flow
Responses from NameNodes are trusted for the shared global maximum. Client-originated state is isolated to the connection pool local accumulator, so a client can only affect later requests sharing the same namespace/UGI pool. Server-side alignment hooks that do not apply to this client-side context are no-ops or unsupported.

## State And Persistence
State is in memory inside two `LongAccumulator` objects. The shared accumulator is held by `RouterStateIdContext`; the pool-local accumulator is scoped to this connection pool. No durable state is written.

## Dependencies And Integration Points
It depends on Hadoop IPC `AlignmentContext` and protobuf RPC headers. `ConnectionPool` uses it for observer-read state propagation; `RouterStateIdContext` supplies namespace-level shared state.

## Risks And Edge Cases
The initial value is `Long.MIN_VALUE`, which is intentionally propagated until a client state is advanced; callers must treat that as "no state" according to the wider alignment protocol. A NameNode response state ID of zero resets accumulated state when global state was positive, preventing stale observer state after alignment is disabled. `isCoordinatedCall` throws because this context should not be used for server-side coordination decisions.

## Test Signals
`TestPoolAlignmentContext` directly verifies pool-local versus shared state separation and reset behavior when NameNodes stop sending state IDs.
