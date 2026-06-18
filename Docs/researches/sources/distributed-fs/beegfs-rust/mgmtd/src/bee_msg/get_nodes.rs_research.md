<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_nodes.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_nodes.rs

**Purpose:** Returns registered nodes of a requested type, including NICs and metadata root information for meta nodes.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `GetNodes`, response `GetNodesResp`; uses `db::node::get_with_type`, `db::node_nic::get_with_type`, `map_bee_msg_nics`, and `db::misc::get_meta_root`.

**Control flow:** Reads nodes, NICs, and meta-root state in one transaction, maps each node to a BeeMsg `Node` with alias bytes, numeric ID, NIC list, and port, sorts by numeric ID, then sets `root_num_id` and `is_root_mirrored` based on `MetaRoot`.

**State and persistence behavior:** Read-only. It exposes current DB node/NIC/root state to peers.

**Dependencies and integration points:** Used by classic clients/servers discovering cluster members. Depends on DB views and shared node types.

**Risks:** NIC mapping filters by node UID for every node, which is simple but can become O(nodes*NICS) for large node lists. Non-meta requests always return root unknown. Alias is encoded as raw bytes.

**Test signals:** Existing `get_nodes` test checks meta-node count and root fields. Add tests for NIC contents and mirrored root behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_nodes.rs -->
