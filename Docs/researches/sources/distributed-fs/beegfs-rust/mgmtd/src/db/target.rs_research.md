<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/target.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/target.rs

Purpose: database operations for metadata and storage targets, including creation, validation, state updates, pool assignment, storage-node mapping, capacity refresh, and deletion.

Important APIs/types/functions: `validate_ids()` verifies target numeric IDs by server node type. `insert_storage()` allocates/creates storage targets. `insert()` creates a target entity and row. `update_consistency_states()`, `update_storage_pools()`, `update_storage_node_mappings()`, `get_and_update_capacities()`, and `delete_storage()` mutate target runtime/assignment state.

Control flow: storage targets can be inserted unmapped; metadata targets are inserted with a node ID. New storage targets default to pool `1`. Capacity refresh reads old capacity values before updating rows and returns the previous values to callers.

State and persistence: writes `entities` and `targets`, including `node_id`, `pool_id`, registration token, consistency, and capacity fields. Deletes storage targets only.

Dependencies and integration points: used by BeeMsg target registration/heartbeat/capacity handlers, gRPC set-state/delete/list/assign, buddy group creation, v7 import, quota target discovery, and timers.

Risks: `insert()` relies on entity alias uniqueness to reject duplicate target aliases; explicit numeric duplicates can still surface as DB constraint errors if not checked by caller. `update_storage_node_mappings()` returns affected count and silently leaves unknown IDs unchanged. Capacity update assumes target rows already exist.

Test signals: unit test covers auto and explicit storage target insertion, duplicate explicit ID failure, mapping updates, and resulting row counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/target.rs -->
