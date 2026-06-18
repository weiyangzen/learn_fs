## sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatMsgEx.h

### Purpose
`HeartbeatMsgEx.h` declares the storage-side heartbeat handler.

### Important APIs, Types, And Functions
The class inherits `HeartbeatMsg` and overrides `processIncoming(ResponseContext&)`.

### Control Flow, State, And Persistence
The header defines no additional state. The base message carries node identity and NIC data used during processing.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the common heartbeat message and the factory maps `NETMSGTYPE_Heartbeat` to this handler. Tests should confirm dispatch and node-store updates through the implementation.
