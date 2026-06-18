## sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatRequestMsgEx.cpp

### Purpose
`HeartbeatRequestMsgEx.cpp` responds to heartbeat requests by sending this storage daemon's current heartbeat information.

### Important APIs, Types, And Functions
`processIncoming()` obtains the local node, local NIC list, and configured storage port, constructs a `HeartbeatMsg` with `NODETYPE_Storage`, sets UDP/TCP ports, sends it as the response, logs the peer IP, and updates heartbeat op stats.

### Control Flow, State, And Persistence
The handler is read-only and sends a full heartbeat response immediately. It does not update node stores because it represents the local node.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on config, local node state, heartbeat messages, and op stats. Risks include stale NIC list or port config at response time. Tests should validate alias, numeric ID, node type, NICs, ports, response send, and stats update.
