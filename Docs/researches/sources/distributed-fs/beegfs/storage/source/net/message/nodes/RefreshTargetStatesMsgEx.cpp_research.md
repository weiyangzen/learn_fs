## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RefreshTargetStatesMsgEx.cpp

### Purpose
`RefreshTargetStatesMsgEx.cpp` handles requests to force a target state refresh.

### Important APIs, Types, And Functions
`processIncoming()` obtains `InternodeSyncer`, calls `setForceTargetStatesUpdate()`, acknowledges the message, and returns true.

### Control Flow, State, And Persistence
The method only changes scheduler state in the syncer. Target state fetching and persistence happen later in internode sync logic.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `InternodeSyncer` and common acknowledgement support. Tests should verify the force-update flag and acknowledgement behavior.
