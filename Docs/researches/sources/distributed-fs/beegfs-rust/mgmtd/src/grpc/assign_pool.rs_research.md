<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/assign_pool.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/assign_pool.rs

Purpose: implements the RPC that assigns a storage pool to selected storage targets and buddy groups.

Important APIs/types/functions: `assign_pool()` performs gRPC-level guards and response shaping. `do_assign()` contains reusable transactional assignment logic shared by `create_pool()`.

Control flow: handler verifies storage-pool license and pre-shutdown state, resolves the pool entity, calls `do_assign()`, logs, and sends `RefreshStoragePools` to meta and storage nodes. `do_assign()` rejects direct target assignment when a target belongs to a storage buddy group, updates standalone target pool IDs, updates buddy group pool IDs, and updates both grouped targets to the same pool.

State and persistence: mutates `targets.pool_id` and `buddy_groups.pool_id` inside the caller's transaction. Sends cluster refresh notifications after commit in the RPC path.

Dependencies and integration points: used by `assign_pool` RPC and `create_pool` RPC. Relies on `ResolveEntityId`, storage pool licensing, SQLite joins over storage buddy groups, and BeeMsg refresh messages.

Risks: partial assignment inside a transaction is safe if the outer transaction rolls back on any error. The function assumes all groups are storage groups via resolved entity semantics and SQL shape; invalid node-type combinations should be tested.

Test signals: no direct tests here. Pool creation/list tests and manual assignment paths should validate grouped target auto-assignment and standalone target rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/assign_pool.rs -->
