<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/storage_pool.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/storage_pool.rs

Purpose: inserts storage-pool entities and rows, including automatic numeric ID allocation.

Important APIs/types/functions: `insert()` accepts an optional numeric `PoolId` (`0` means auto), validates uniqueness, creates a global pool entity with the supplied alias, inserts into `pools`, and returns `(Uid, PoolId)`.

Control flow: auto-ID uses `misc::find_new_id()` against the `pools` table for storage node type. Explicit IDs are checked via `try_resolve_num_id()`. After entity insertion, the concrete pool row is inserted with storage node type.

State and persistence: writes `entities` and `pools`; assignment of targets or buddy groups to the pool is handled by gRPC `assign_pool`/`create_pool` logic, not here.

Dependencies and integration points: used by `grpc/create_pool.rs` and v7 storage-pool import. It depends on entity uniqueness, SQLite enum mapping, and typed value-exists errors.

Risks: entity insertion and pool insertion must be in one transaction to avoid orphaned entities on failure. Pool ID range is fixed to 16-bit-like `1..=0xFFFF`.

Test signals: no local tests in this file; create/list pool gRPC tests and v7 importer tests exercise the path indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/storage_pool.rs -->
