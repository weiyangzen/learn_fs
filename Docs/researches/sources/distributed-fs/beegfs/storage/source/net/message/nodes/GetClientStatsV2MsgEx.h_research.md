## sources/distributed-fs/beegfs/storage/source/net/message/nodes/GetClientStatsV2MsgEx.h

### Purpose
`GetClientStatsV2MsgEx.h` declares the storage-side client statistics request handler.

### Important APIs, Types, And Functions
The class inherits `GetClientStatsV2Msg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No extra state is defined. The request fields from the base control stats export behavior.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common storage errors and the common node stats request. Tests should confirm factory creation and stats response behavior through the implementation.
