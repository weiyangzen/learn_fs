<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNode.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/LocalNode.h

### Purpose
`LocalNode` represents the current service as a `Node` while using a special local connection pool for in-process/internal communication.

### Important APIs, Types, And Functions
It derives from `Node`. The constructor calls the protected `Node` constructor and installs a `LocalNodeConnPool`. `getPortTCP()` overrides the node TCP port to return `0`, reflecting internal local communication rather than a network stream port.

### Control Flow
Construction sets up local-node identity and attaches an internal connection pool built from the local NIC list.

### State, Persistence, And Dependencies
State is inherited node identity plus a local connection pool. It depends on `LocalNodeConnPool`, `NodeConnPool`, and `Node`.

### Integration Points
Services use `LocalNode` when inserting themselves into node stores and routing self-directed messages internally.

### Risks
Returning TCP port `0` is intentional but can surprise code that treats all nodes as network peers. Tests should cover self-message routing and node serialization paths that include a local node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNode.h -->
