<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_storage_target_info.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_storage_target_info.rs

**Purpose:** Updates stored capacity information for meta or storage targets.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `SetStorageTargetInfo`, response `SetStorageTargetInfoResp`, error response `OpsErr::INTERNAL`; uses `db::target::get_and_update_capacities` and `TargetCapacities`.

**Control flow:** Fails during pre-shutdown, converts each reported capacity entry into optional `u64` totals/free values, updates capacities for the requested node type in a write transaction, logs the update, and returns `SUCCESS`.

**State and persistence behavior:** Mutates target capacity columns (`total_space`, `total_inodes`, `free_space`, `free_inodes`). It does not immediately notify capacity-pool refreshes, relying on periodic node refresh behavior.

**Dependencies and integration points:** Feeds capacity data consumed by capacity pool handlers and storage pool responses.

**Risks:** Numeric conversion failures reject the whole update. The comment notes old management sent refresh notifications when cap pools changed, but this implementation avoids that cost, so peers can observe delayed capacity pool changes.

**Test signals:** Update capacities for known targets, verify DB values and downstream capacity pool responses; test conversion failure and pre-shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_storage_target_info.rs -->
