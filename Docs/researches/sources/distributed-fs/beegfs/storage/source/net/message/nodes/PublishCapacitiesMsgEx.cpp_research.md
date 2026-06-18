## sources/distributed-fs/beegfs/storage/source/net/message/nodes/PublishCapacitiesMsgEx.cpp

### Purpose
`PublishCapacitiesMsgEx.cpp` handles a management request to force capacity publication from the storage daemon.

### Important APIs, Types, And Functions
`processIncoming()` retrieves `InternodeSyncer`, calls `setForcePublishCapacities()`, acknowledges the request, and returns true.

### Control Flow, State, And Persistence
The handler mutates syncer scheduling state only; the actual capacity publication occurs asynchronously in the internode syncer.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `InternodeSyncer` and acknowledgement semantics. Risks are low; repeated requests only set a force flag. Tests should verify the force flag and acknowledgement.
