<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/Node.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/Node.h

### Purpose
`Node.h` declares the common representation of a BeeGFS service node, including identity, connection pool access, heartbeat time, port/NIC data, and serialization helpers for vectors of node handles.

### Important APIs, Types, And Functions
`Node` stores alias, numeric ID, node type, `NodeConnPool*`, UDP port, heartbeat time, and alias mutex. Public APIs expose heartbeat, interface updates, typed ID strings, alias/ID/port/NIC/pool getters and setters. `VectorDes` deserializes node vectors in old and v6 formats; global `operator%` serializes/deserializes `std::vector<NodeHandle>`. `inV6Format()` selects the v6 deserialization layout.

### Control Flow
Vector serialization writes count then alias, NIC list, numeric ID, UDP/TCP ports, and node type for each node. v6 deserialization reads count plus padding, then feature flags, aligned string ID, NIC list, version, IDs, ports, and node type, creating `Node` objects.

### State, Persistence, And Dependencies
Node state is in-memory; serialized vectors are exchanged over management and heartbeat messages. Dependencies include `NumNodeID`, `Condition`, `BitStore`, serialization helpers, `Time`, `NodeConnPool`, `NodeType`, and `NetworkInterfaceCard`.

### Integration Points
Node stores and management messages serialize node lists through these operators. Connection code uses `getConnPool()` to communicate with nodes.

### Risks
Serialization constructs full `NodeConnPool` instances for deserialized nodes, so NIC and port correctness matters. `VectorDes::runV6()` reads fields it does not store, such as feature flags/version. Alias locking does not cover numeric ID changes. Tests should cover old/v6 node vector round-trips, malformed counts, NIC list parsing, alias updates, and port getters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/Node.h -->
