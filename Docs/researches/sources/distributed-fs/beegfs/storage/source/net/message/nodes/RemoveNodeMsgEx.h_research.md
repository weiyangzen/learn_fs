## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveNodeMsgEx.h

### Purpose
`RemoveNodeMsgEx.h` declares the storage-side node removal handler.

### Important APIs, Types, And Functions
The class inherits `RemoveNodeMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is defined. Processing mutates node stores based on inherited node type and numeric ID fields.

### Dependencies, Integration Points, Risks, And Test Signals
It is instantiated for `NETMSGTYPE_RemoveNode`. Tests should verify factory dispatch and storage-node removal semantics.
