<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/change_target_consistency_states.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/change_target_consistency_states.rs

**Purpose:** Handles conditional consistency-state transitions reported by nodes for multiple targets.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `ChangeTargetConsistencyStates`, response `ChangeTargetConsistencyStatesResp`, and error response `OpsErr::INTERNAL`. Uses `fail_on_pre_shutdown`, `db::target::validate_ids`, `common::update_last_contact_times`, and `db::target::update_consistency_states`.

**Control flow:** Rejects during pre-shutdown, verifies target/new/old list lengths, validates target IDs, updates contact times, compares every reported old state to the stored state, and only applies new states if all old states match. It returns `SUCCESS` when applied and `AGAIN` when old-state mismatch prevents changes. Refresh notifications are sent to meta, storage, and client nodes only when consistency or reachability changed.

**State and persistence behavior:** Updates `nodes.last_contact`, `targets.last_update`, and target consistency rows in SQLite. Sends `RefreshTargetStates` notifications as an external state synchronization signal.

**Dependencies and integration points:** Used for target state coordination in the classic BeeMsg path. Depends on config `node_offline_timeout`, target DB schema, and notification broadcasts.

**Risks:** Mismatched old state aborts all consistency changes but contact times may already have been updated. The all-or-nothing policy is safer but can defer legitimate partial updates. List-length mismatch is a hard error and maps to the generic internal response.

**Test signals:** Existing tests cover reachability notification, consistency updates, database counts, and old-state mismatch returning `AGAIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/change_target_consistency_states.rs -->
