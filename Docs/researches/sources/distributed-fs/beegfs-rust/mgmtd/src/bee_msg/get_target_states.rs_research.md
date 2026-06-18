<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_target_states.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_target_states.rs

**Purpose:** Returns target IDs and parallel arrays of consistency and reachability states for a requested node type.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `GetTargetStates`, response `GetTargetStatesResp`; uses `common::get_targets_with_states`.

**Control flow:** Captures pre-shutdown state and offline timeout, reads computed target states, then splits each tuple into `targets`, `consistency_states`, and `reachability_states` vectors.

**State and persistence behavior:** Read-only. Reachability is computed dynamically from DB timestamps and run state.

**Dependencies and integration points:** Used by classic peers for state refresh. Integrates with notification-triggered refreshes from state-mutating handlers.

**Risks:** Parallel vector alignment is critical. Query ordering is not explicitly defined. Pre-shutdown can mark non-secondary targets probably offline.

**Test signals:** Validate equal vector lengths, alignment, offline threshold behavior, and pre-shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_target_states.rs -->
