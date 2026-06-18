<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_states_and_buddy_groups.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_states_and_buddy_groups.rs

**Purpose:** Returns combined target reachability/consistency state plus buddy group topology in one response.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `GetStatesAndBuddyGroups`, response `GetStatesAndBuddyGroupsResp`; uses `common::get_targets_with_states` and `app.notify_client_pulled_state`.

**Control flow:** Converts the requested node type, captures pre-shutdown and offline timeout, reads target states and buddy groups in a transaction, builds maps of target ID to `CombinedTargetState` and group ID to `BuddyGroup`, and notifies the run controller when a client ID is present.

**State and persistence behavior:** Read-only DB access. During pre-shutdown it may emit an in-memory notification that a client pulled state, used for shutdown coordination.

**Dependencies and integration points:** Integrates target-state computation, buddy group DB view, and run-state shutdown behavior in `RuntimeApp`.

**Risks:** Pre-shutdown changes reported reachability semantics through `get_targets_with_states`. Client pull notification is best-effort in runtime and no-op in tests. HashMap ordering is not deterministic.

**Test signals:** Validate maps for seeded target/group data, pre-shutdown reachability behavior, and client notification on nonzero `requested_by_client_id`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_states_and_buddy_groups.rs -->
