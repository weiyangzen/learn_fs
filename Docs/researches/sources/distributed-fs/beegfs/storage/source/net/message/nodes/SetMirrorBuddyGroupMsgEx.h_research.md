## sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h

### Purpose
`SetMirrorBuddyGroupMsgEx.h` declares the storage-side mirror buddy group mapping handler.

### Important APIs, Types, And Functions
The class derives from `SetMirrorBuddyGroupMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The handler has no additional state; inherited group/target fields drive mapper updates.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_SetMirrorBuddyGroup`. Tests should validate mapper mutation and response semantics in the implementation.
