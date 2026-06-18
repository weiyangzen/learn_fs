## sources/distributed-fs/beegfs/client_module/source/nodes/NodeStoreEx.c

**Purpose:** Implements a thread-safe kernel client node store for metadata/storage/management nodes. It tracks active nodes by numeric ID, updates aliases/interfaces on heartbeat/list refreshes, handles root metadata owner selection, references nodes safely, and synchronizes the store against ordered master lists.

**Important APIs/types/functions:** Key functions are `NodeStoreEx_init`, `construct`, `uninit`, `addOrUpdateNode`, `referenceNode`, `referenceRootNode`, `referenceNodeByTargetID`, `deleteNode`, `getSize`, `referenceFirstNode`, `referenceNextNodeAndReleaseOld`, `getRootOwner`, `setRootOwner`, `waitForFirstNode`, `syncNodes`, and `__NodeStoreEx_handleNodeVersion`.

**Control flow:** Adds/updates take the write lock, reject numeric ID 0, find existing nodes, update aliases when non-empty incoming aliases differ, clone/update NIC lists and heartbeat time, or insert new nodes and mark them active. References take the read lock, find a node, increment its kref, and return it for later `Node_put`. Root references resolve mirror buddy groups to primary target IDs before looking up the node. `syncNodes` compares sorted active/master iterators under lock to compute added/removed IDs, then unlocks and performs deletion/addition in a second phase to avoid virtual-method style reentrancy issues.

**State and persistence behavior:** The store maintains in-memory `NodeTree`, `RWLock`, optional `newNodeAppeared` completion pointer, `_rootOwner`, and `storeType`. Node additions consume ownership of the incoming node pointer and null it. Deletions erase from the active tree and rely on node reference counting for lifetime. No persistent configuration is written here; it reflects management-provided cluster state.

**Dependencies and integration points:** Uses `App` logging and buddy mapper, `Node`, `NodeTree`, `NodeList`, `TargetMapper`, NIC capability helpers, `RWLock`, kernel completions, and `MirrorBuddyGroupMapper`. Remoting paths use node stores to route request/response traffic and stat root.

**Risks:** Callers must release referenced nodes or leak refs; debug builds warn on very high reference counts. `waitForFirstNode` supports a single waiter through `newNodeAppeared` and warns if reused concurrently. `syncNodes` assumes the master list is ordered and removes nodes from it while building `addLaterNodes`. Root buddy resolution depends on up-to-date buddy mappings.

**Test signals:** Test add/update alias changes, invalid ID rejection, NIC update behavior, reference/release lifetime, root owner direct and mirrored lookup, target-ID mapping failures, wait-for-first-node timeout and completion, sorted sync add/remove/unchanged cases, and concurrent readers during updates/deletes.
