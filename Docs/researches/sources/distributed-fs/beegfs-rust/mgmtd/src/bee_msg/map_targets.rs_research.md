<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/map_targets.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/map_targets.rs

**Purpose:** Maps storage targets to a storage node and notifies the cluster.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `MapTargets`, response `MapTargetsResp`; uses `LegacyId::resolve`, `db::target::validate_ids`, `db::target::update_storage_node_mappings`, and `RefreshStoragePools`.

**Control flow:** Fails during pre-shutdown, collects target IDs, validates the storage node and all targets, updates mappings in one write transaction, sends `MapTargets` notifications to meta/storage/client nodes, sends `RefreshStoragePools` to meta/storage when mappings changed, and returns per-target `SUCCESS` results.

**State and persistence behavior:** Mutates storage target node mappings in SQLite. Broadcast notifications synchronize peers and trigger pool refreshes.

**Dependencies and integration points:** Integrates with storage registration/mapping, storage pool membership, and classic peer update notifications.

**Risks:** All-or-nothing validation means one bad target ID fails the whole request. The response reports success for every requested target only after the transaction succeeds; failure details are generic through dispatcher error handling.

**Test signals:** Map multiple targets, verify DB mappings, `MapTargets` notifications, conditional `RefreshStoragePools`, and invalid node/target failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/map_targets.rs -->
