<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/heartbeat.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/heartbeat.rs

**Purpose:** Processes incoming node heartbeats as node updates and returns an acknowledgement.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `Heartbeat`, response `misc::Ack`; converts heartbeat fields into a `RegisterNode` and calls `common::update_node`.

**Control flow:** Fails during pre-shutdown, wraps heartbeat node data in `RegisterNode`, calls `update_node` with `reject=false`, then returns `Ack { ack_id }`.

**State and persistence behavior:** Updates node registration data, NICs, target/root state for meta nodes, contact/address state, and sends heartbeat notifications via `update_node`.

**Dependencies and integration points:** Shares registration logic with explicit `RegisterNode`. Used by recurring classic heartbeats from nodes.

**Risks:** Because `reject=false`, client license exhaustion logs but may not reject legacy clients. Heartbeat updates use no-sync writes through `update_node`.

**Test signals:** Heartbeat should update existing node contact/NIC/address data and return matching ack ID; pre-shutdown should produce generic TRY_AGAIN at dispatch level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/heartbeat.rs -->
