## sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.cpp

### Purpose
`SetTargetConsistencyStatesMsgEx.cpp` applies requested consistency states to local storage targets.

### Important APIs, Types, And Functions
`processIncoming()` validates that `getTargetIDs()` and `getStates()` have equal length, iterates them with `ZipIterRange`, resolves each `StorageTarget`, calls `target->setState(TargetConsistencyState(...))`, and replies with `SetTargetConsistencyStatesRespMsg`.

### Control Flow, State, And Persistence
The operation is sequential and stops at the first list-size mismatch or unknown target. Runtime target consistency state is mutated; persistence depends on `StorageTarget::setState()` internals outside this file.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageTargets`, common response messages, and `ZipIterator`. Risks include partial updates before a later unknown target, no validation that state byte values are valid enum members, and all-or-first-error response semantics. Tests should cover length mismatch, unknown target, multiple target update, invalid state value, and response result codes.
