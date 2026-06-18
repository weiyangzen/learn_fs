<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_pool.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_pool.rs

Purpose: deletes an empty storage pool.

Important APIs/types/functions: `delete_pool()` resolves the pool entity, counts assigned storage targets and buddy groups, deletes the pool row when empty, and returns the deleted pool entity.

Control flow: after license/pre-shutdown checks, an immediate transaction enforces emptiness. The `execute` flag controls commit. Successful execution logs and sends `RefreshStoragePools` to meta and storage nodes.

State and persistence: removes from `pools`; entity cleanup depends on schema behavior. It does not reassign targets or groups.

Dependencies and integration points: storage-pool license, entity resolution, SQLite pool/target/group tables, and storage-pool refresh.

Risks: default pool deletion behavior is governed only by DB constraints and assigned rows; this file does not special-case pool ID 1. Dry-run mode executes deletion inside a rolled-back transaction.

Test signals: no direct tests. Useful coverage would include non-empty pool rejection, execute=false no-op, default pool handling, and notification emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_pool.rs -->
