<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_target_consistency_states.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_target_consistency_states.rs

**Purpose:** Sets target consistency states unconditionally and optionally refreshes contact times.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `SetTargetConsistencyStates`, response `SetTargetConsistencyStatesResp`, error response `OpsErr::INTERNAL`; uses `update_last_contact_times` and `db::target::update_consistency_states`.

**Control flow:** Fails during pre-shutdown, converts node type, clones the message for transaction use, validates target IDs, updates last-contact times when `set_online > 0`, writes new consistency states, logs, broadcasts `RefreshTargetStates` to meta/storage/client nodes, and returns `SUCCESS`.

**State and persistence behavior:** Mutates target consistency and optionally node/target contact timestamps. Broadcasts refresh notifications regardless of whether actual values changed.

**Dependencies and integration points:** Used by classic target state management and peer refresh mechanisms.

**Risks:** Does not validate that `target_ids` and `states` have equal length before zipping; extra IDs or states may be ignored by `update_consistency_states` depending on implementation. Always notifies, which can produce unnecessary refresh traffic.

**Test signals:** Test equal and mismatched vector lengths, `set_online` timestamp updates, DB consistency changes, notifications, and invalid target errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_target_consistency_states.rs -->
