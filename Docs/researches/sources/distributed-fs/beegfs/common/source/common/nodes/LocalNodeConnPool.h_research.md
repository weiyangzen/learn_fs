<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.h

### Purpose
`LocalNodeConnPool.h` declares the local/internal connection pool used by `LocalNode`.

### Important APIs, Types, And Functions
It derives from `NodeConnPool`, defines `UnixConnWorkerList`, and overrides `acquireStreamSocketEx()`, `releaseStreamSocket()`, `invalidateStreamSocket()`, and `updateInterfaces()`. It stores a list of `UnixConnWorker*` and a creation counter.

### Control Flow
The pool follows the same acquire/release contract as network node pools while creating local worker endpoints.

### State, Persistence, And Dependencies
State is in-memory local worker ownership. It depends on `NodeConnPool`, `LocalConnWorker`, and node/socket types.

### Integration Points
`LocalNode` uses it to avoid network paths for self-directed messaging.

### Risks
The class owns raw worker pointers, so destructor/invalidation correctness is important. Tests should verify ownership cleanup and polymorphic behavior through `NodeConnPool*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.h -->
