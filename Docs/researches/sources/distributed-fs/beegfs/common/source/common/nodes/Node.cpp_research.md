<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/Node.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/Node.cpp

### Purpose
`Node.cpp` implements construction, heartbeat tracking, interface updates, and display-name formatting for BeeGFS nodes.

### Important APIs, Types, And Functions
The main constructor initializes node type, alias, numeric ID, UDP port, and allocates a `NodeConnPool`. The protected constructor supports subclasses such as `LocalNode` that install their own pool. `updateLastHeartbeatT()` and `getLastHeartbeatT()` guard `Time lastHeartbeatT` with `mutex`. `updateInterfaces()` updates UDP port and delegates stream/NIC changes to the connection pool. `getTypedNodeID()` and `getNodeIDWithTypeStr()` build log-friendly identity strings under `aliasMutex`.

### Control Flow
Interface updates preserve the old UDP port when passed zero and return the connection pool's update result. The destructor deletes the connection pool.

### State, Persistence, And Dependencies
Node identity, ports, heartbeat, alias, and connection pool are in-memory state. Dependencies include `NodeConnPool`, `Socket`, `Time`, mutexes, shared mutexes, and `boost::format`.

### Integration Points
Node stores, messaging, heartbeat processing, debug output, and management logs use `Node`.

### Risks
`numID` changes are not guarded by `aliasMutex` or `mutex`, while formatted ID methods read it under only the alias lock. Raw `NodeConnPool*` ownership requires derived classes to set it correctly. Tests should cover construction/destruction, subclass pool installation, heartbeat updates, port-zero preservation, alias concurrent reads/writes, and identity string formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/Node.cpp -->
