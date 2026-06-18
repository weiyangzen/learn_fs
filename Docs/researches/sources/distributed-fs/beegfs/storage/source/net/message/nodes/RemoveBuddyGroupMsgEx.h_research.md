## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveBuddyGroupMsgEx.h

### Purpose
`RemoveBuddyGroupMsgEx.h` declares the storage-side mirror buddy group removal handler.

### Important APIs, Types, And Functions
The class derives from `RemoveBuddyGroupMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The handler has no additional data members; inherited fields such as group ID, node type, force, and check-only drive processing.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_RemoveBuddyGroup`. Tests should validate response codes and mapper changes through the implementation.
