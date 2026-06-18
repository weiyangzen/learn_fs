## sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatRequestMsgEx.h

### Purpose
`HeartbeatRequestMsgEx.h` declares the storage-side heartbeat request responder.

### Important APIs, Types, And Functions
The class derives from `HeartbeatRequestMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
No additional state is stored. The handler synthesizes a heartbeat from app-local node/config state.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_HeartbeatRequest`. Tests should confirm the response message fields and virtual dispatch.
