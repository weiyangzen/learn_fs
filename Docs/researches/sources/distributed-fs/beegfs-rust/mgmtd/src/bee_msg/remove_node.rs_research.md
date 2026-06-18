<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/remove_node.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/remove_node.rs

**Purpose:** Handles classic node-removal requests, currently restricted to client nodes.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `RemoveNode`, response `RemoveNodeResp`, error response `OpsErr::INTERNAL`; uses `LegacyId::resolve` and `db::node::delete`.

**Control flow:** Fails during pre-shutdown, rejects non-client node types with an instruction that server-node deletion must use gRPC, resolves the client node, deletes it in a write transaction, logs deletion, broadcasts `RemoveNode` notifications based on node type, and returns `SUCCESS`.

**State and persistence behavior:** Deletes node rows and related DB state via `db::node::delete`. Broadcast side effects are limited because the only allowed type is client, and the notification match sends to no node types for clients.

**Dependencies and integration points:** Classic cleanup path for client nodes. Server-node removal belongs to the gRPC management API.

**Risks:** The post-delete notification match includes meta/storage cases unreachable under current validation, which can confuse future maintenance. All errors become internal responses unless the dispatcher special-cases them.

**Test signals:** Remove a client node and verify DB deletion; attempt meta/storage removal and verify failure; dispatch pre-shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/remove_node.rs -->
