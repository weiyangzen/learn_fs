## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetTargetConsistencyStatesMsgEx.cpp

### Purpose
`GetTargetConsistencyStatesMsgEx.cpp` returns the storage daemon's current consistency state for requested target IDs.

### Important APIs, Types, And Functions
`processIncoming()` obtains `StorageTargets`, transforms `targetIDs` into a `TargetConsistencyStateVec`, maps unknown targets to `TargetConsistencyState_BAD`, and sends `GetTargetConsistencyStatesRespMsg`.

### Control Flow, State, And Persistence
The handler is read-only. It preserves request order in the returned state vector.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageTargets` and common target-state response messages. Risks include treating unknown targets as BAD rather than returning an explicit error, which callers must interpret correctly. Tests should cover known good/needs-resync/bad states, unknown target IDs, empty requests, and response order.
