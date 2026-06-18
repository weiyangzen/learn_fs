<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/common.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/common.rs

**Purpose:** Shared helper logic for BeeMsg handlers, especially node registration/update and target reachability/contact-state calculations.

**Important APIs/types/functions:** Defines `MAX_NUM_CLIENTS = 5`, `update_node`, `get_targets_with_states`, and `update_last_contact_times`. `update_node` processes `RegisterNode`-shaped information, handles licensing, registration disable rules, aliases/tokens, node insert/update, meta target auto-creation, NIC replacement, root inode selection, address replacement, and heartbeat notifications.

**Control flow:** `update_node` calculates client/license limits, opens a no-sync write transaction, resolves existing node IDs, validates machine UUID licensing for meta/storage nodes, updates or inserts nodes, enforces registration tokens for meta targets, auto-creates a meta target and first root inode for new meta nodes, replaces NIC rows, reads meta-root state, then updates the connection pool and sends heartbeat notifications to interested node types. `get_targets_with_states` joins targets/nodes/buddy groups and derives reachability from pre-shutdown state, buddy role, and offline timeout. `update_last_contact_times` updates node/target timestamps and returns how many targets crossed the probably-offline threshold.

**State and persistence behavior:** Mutates nodes, targets, meta targets, root inode, NICs, and contact timestamps. It also updates in-memory connection addresses and broadcasts heartbeat notifications. Registration token and alias handling persist identity constraints.

**Dependencies and integration points:** Used by `RegisterNode`, `Heartbeat`, state query/update handlers, and notification paths. Depends on DB modules, license verification protobuf results, `sqlite_check::sql!`, shared BeeMsg node/target types, and app config.

**Risks:** No-sync writes trade durability for speed during node updates. License fallback behavior differs by failure mode: valid license means unlimited clients, missing/errored license limits clients, invalid license does not limit in this code path. Meta node numeric IDs must fit target IDs, and registration token mismatch fails updates. Reachability logic has special cases for primary buddy targets and pre-shutdown.

**Test signals:** Handler tests indirectly cover portions. Focused tests should cover new/existing node registration, registration-disabled behavior, client license limits with/without rejection flag, meta target auto-creation, token mismatch, NIC replacement, root inode reporting, and reachability transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/common.rs -->
