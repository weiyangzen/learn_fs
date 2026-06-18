<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/AbstractNodeStore.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/AbstractNodeStore.h

### Purpose
`AbstractNodeStore` defines the common interface for stores of BeeGFS nodes such as metadata, storage, management, and clients.

### Important APIs, Types, And Functions
It declares `NodeStoreResult` values `Unchanged`, `Added`, `Updated`, and `Error`. Virtual methods include `addOrUpdateNode()`, `addOrUpdateNodeEx()`, `referenceFirstNode()`, `referenceAllNodes()`, and `getSize()`. The protected `NodeMap` maps `NumNodeID` to `shared_ptr<Node>`.

### Control Flow
Concrete stores implement insertion/update semantics and reference retrieval. The protected constructor fixes the `NodeType` applied to contained nodes.

### State, Persistence, And Dependencies
The abstract base stores only `storeType`; concrete stores manage node maps. It depends on `Node`, `NumNodeID`, and shared pointer ownership.

### Integration Points
Messaging, management, heartbeat, and debug code interact with node stores through this abstraction.

### Risks
Reference-returning methods must define thread-safety and lifetime in concrete stores. Tests should cover concrete store add/update result transitions, first/all references, and type enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/AbstractNodeStore.h -->
