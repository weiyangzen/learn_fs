<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/refresh_capacity_pools.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/refresh_capacity_pools.rs

**Purpose:** Acknowledges but ignores requests asking management to refresh capacity pools.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `RefreshCapacityPools`, response `Ack`.

**Control flow:** Returns `Ack { ack_id }` immediately. Comment explains capacity-pool pulls are handled through target info updates instead.

**State and persistence behavior:** No DB or in-memory state changes.

**Dependencies and integration points:** Registered for compatibility with meta/storage nodes that send this classic message on startup.

**Risks:** Peers expecting immediate management-side recalculation may see stale capacity pools until periodic/node-driven refreshes happen.

**Test signals:** Dispatch message and verify ack ID is preserved and no DB mutation occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/refresh_capacity_pools.rs -->
