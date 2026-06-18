## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RefreshTargetStatesMsgEx.h

### Purpose
`RefreshTargetStatesMsgEx.h` declares the storage-side target-state refresh trigger.

### Important APIs, Types, And Functions
The class inherits `RefreshTargetStatesMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The header has no state; the implementation sets an internode syncer flag.

### Dependencies, Integration Points, Risks, And Test Signals
It is created by the message factory for `NETMSGTYPE_RefreshTargetStates`. Tests should cover dispatch and ack.
