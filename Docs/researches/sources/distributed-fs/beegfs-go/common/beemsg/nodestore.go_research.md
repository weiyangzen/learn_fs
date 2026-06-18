<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/nodestore.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/nodestore.go

Purpose: thread-safe in-memory registry of BeeGFS nodes, aliases, legacy IDs, root metadata identity, buddy group metadata, and reusable TCP connections.

Important APIs/types/functions: `NodeStore`, `NewNodeStore`, `Cleanup`, `AddNode`, `SetMetaRootNode`, `GetMetaRootNode`, `SetMetaRootBuddyGroup`, `GetMetaRootBuddyGroup`, `HasMetaRootBuddyGroup`, `GetNode`, `GetNodes`, `RequestTCP`, `RequestUDP`, `getNodeAndConns`, and `resolveEntityId`.

Control flow: `AddNode` rejects duplicate UID, alias, legacy node ID, and connection-store entries before creating a `util.NodeConns`. Public getters resolve `beegfs.EntityId` by type under an RW mutex and return clones. TCP/UDP request methods resolve the node and connection pool under lock, release the lock, then perform network I/O.

State and persistence: all state is process-local maps and connection queues. `Cleanup` closes pooled TCP sockets. Root metadata and buddy group getters return clones to avoid caller mutation.

Dependencies and integration points: depends on `common/beegfs`, message interfaces, and `beemsg/util` connection helpers. It is the main integration layer between node metadata discovery and BeeMsg transport.

Risks: `Cleanup` iterates `connsByUid` without taking the store lock; callers must coordinate shutdown. `SetMetaRootBuddyGroup` assigns `nil` for UID 0 but then immediately assigns `&rootMirror`, so UID 0 does not clear as intended. `resolveEntityId` accepts raw `Uid` without checking node type. `GetNodes` order is map-random.

Test signals: `nodestore_test.go` covers add/get, duplicate rejection, entity ID resolution, node list length, and root metadata node validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/nodestore.go -->
