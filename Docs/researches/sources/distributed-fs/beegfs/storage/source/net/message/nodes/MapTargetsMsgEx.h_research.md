## sources/distributed-fs/beegfs/storage/source/net/message/nodes/MapTargetsMsgEx.h

### Purpose
`MapTargetsMsgEx.h` declares the storage-side target mapping handler.

### Important APIs, Types, And Functions
The class inherits `MapTargetsMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional handler state is stored; inherited target mappings drive mapper mutations.

### Dependencies, Integration Points, Risks, And Test Signals
It is created for `NETMSGTYPE_MapTargets`. Tests should validate factory routing and mapper updates through the implementation.
