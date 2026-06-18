<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/ack.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/ack.rs

**Purpose:** Handles incoming BeeMsg `Ack` messages that require no management action.

**Important APIs/types/functions:** Implements `HandleNoResponse` for `shared::bee_msg::misc::Ack`.

**Control flow:** Logs the remote address and `ack_id` at debug level, then returns success without responding.

**State and persistence behavior:** No state changes or persistence.

**Dependencies and integration points:** Registered in the central BeeMsg dispatcher. Used as a sink for acknowledgements from peers and as a response type in other handlers.

**Risks:** Any Ack semantics beyond observability are intentionally ignored; if a future peer expects ack correlation, this handler would need state.

**Test signals:** Dispatch an `Ack` through the BeeMsg dispatcher and verify no response or database mutation occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/ack.rs -->
