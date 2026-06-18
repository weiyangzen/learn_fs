<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_target_state.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_target_state.rs

Purpose: manually updates a target consistency state and pushes that state to the owning node.

Important APIs/types/functions: `set_target_state()` parses target entity and desired `TargetConsistencyState`, updates the DB through `db::target::update_consistency_states()`, sends `SetTargetConsistencyStates` to the target owner, and broadcasts `RefreshTargetStates`.

Control flow: DB state is updated first and returns the target plus node UID. Then the handler sends the node request and bails if the response is not `OpsErr::SUCCESS`. Finally, all meta/storage/client nodes are notified to refresh target states.

State and persistence: mutates `targets.consistency`. The node-side state update and cluster refresh are separate network side effects.

Dependencies and integration points: pre-shutdown guard, target entity resolution, target DB helper, BeeMsg target-state messages, and refresh notifications.

Risks: if the DB update succeeds but the node request fails, the handler returns an error while DB state remains changed. This asymmetry is explicitly called out in the error message and may need operator attention.

Test signals: no direct tests. Useful tests would simulate node success/failure, unknown target, meta/storage state mapping, and notification emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_target_state.rs -->
