<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_pool.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_pool.rs

Purpose: implements storage pool creation and optional initial assignment of targets and buddy groups.

Important APIs/types/functions: `create_pool()` validates the request is for storage node type, parses alias and optional numeric pool ID, calls `db::storage_pool::insert()`, then reuses `assign_pool::do_assign()`.

Control flow: license and pre-shutdown guards run first. The DB transaction inserts the pool and applies requested assignments atomically. The handler builds a `EntityIdSet`, logs, sends `RefreshStoragePools` to meta/storage nodes, and returns the pool.

State and persistence: writes `entities` and `pools`, and may update `targets.pool_id` and `buddy_groups.pool_id`.

Dependencies and integration points: storage-pool license, pool DB helpers, assignment logic, and BeeMsg storage-pool refresh.

Risks: node type must be storage; any future non-storage pool type would require API changes. Assignment validation can fail after pool insertion but before commit, which is safe because the transaction rolls back.

Test signals: `get_pools` tests validate fixture pools; create-pool-specific tests would be useful for auto IDs, assignment rollback, and notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_pool.rs -->
