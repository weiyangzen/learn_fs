## sources/distributed-fs/beegfs/storage/source/net/message/nodes/HeartbeatMsgEx.cpp

### Purpose
`HeartbeatMsgEx.cpp` handles incoming node heartbeat messages and updates the storage daemon's node stores. It discovers or refreshes meta, management, and storage nodes.

### Important APIs, Types, And Functions
`processIncoming()` builds a `Node` from heartbeat fields and NIC list, applies local NIC capabilities to its connection pool, selects the appropriate `AbstractNodeStore` by node type, calls `addOrUpdateNode()`, logs newly added nodes and RDMA support, acknowledges the message, and updates `StorageOpCounter_HEARTBEAT`.

### Control Flow, State, And Persistence
Invalid node types are logged and still fall through to acknowledgement. Node store membership is persistent runtime cluster state. The method moves the constructed node into the selected store.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on network interface capability helpers, node stores, `Node`, acknowledgement support, and op stats. Risks include acknowledging invalid node types, stale NIC capability assumptions, and node identity conflicts handled by the store. Tests should cover each node type, invalid type, new versus update logging, RDMA NIC detection, and acknowledgement behavior.
