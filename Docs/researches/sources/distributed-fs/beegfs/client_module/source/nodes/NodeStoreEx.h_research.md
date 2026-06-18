## sources/distributed-fs/beegfs/client_module/source/nodes/NodeStoreEx.h

**Purpose:** Declares `NodeStoreEx`, the kernel client node-store abstraction corresponding to userspace node stores, with APIs for insertion, lookup, iteration, root-owner tracking, waiting, and synchronization.

**Important APIs/types/functions:** Defines `struct NodeStoreEx` with `App*`, `RWLock`, optional completion pointer, `NodeTree`, `_rootOwner`, and `storeType`. Declares all lifecycle and lookup/sync functions plus inline `NodeStoreEx_getStoreType`.

**Control flow:** Callers construct/init a store for a `NodeType`, add or update owned `Node*` instances, reference nodes by numeric ID or target ID, iterate by first/next, and synchronize against management lists. The header's contract makes reference ownership explicit: returned nodes require later release.

**State and persistence behavior:** State is in-memory only and protected by `rwLock`. `_rootOwner` may represent a direct node or mirror buddy group. The store type is applied to nodes when they enter the store.

**Dependencies and integration points:** Pulls in BeeGFS logging, `App`, lists, `EntryInfo`, storage errors, threading primitives, `Node`, `NodeTree`, `TargetMapper`, and kernel completion/rwsem headers. It is consumed by app initialization, management synchronization, and remoting routing.

**Risks:** The header declares `NodeStoreEx_referenceNextNode` but the inspected `.c` file implements `referenceNextNodeAndReleaseOld`; callers or other translation units must provide/use the correct symbol. Incorrect release discipline can leak or prematurely drop node references. `_rootOwner` validity relies on `NodeOrGroup` semantics outside this file.

**Test signals:** Build all users to catch declaration/definition drift, run lockdep/concurrency tests for reference and sync operations, and validate root-owner state transitions.
