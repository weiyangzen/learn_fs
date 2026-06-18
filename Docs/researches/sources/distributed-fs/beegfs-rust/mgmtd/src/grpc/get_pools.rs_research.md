<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_pools.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_pools.rs

Purpose: returns storage pools with assigned storage targets, buddy groups, and optionally default quota limits.

Important APIs/types/functions: `get_pools()` builds pool records from storage pool tables, joins default quota limits when requested, separately gathers target and buddy-group assignments, then merges them into each pool response.

Control flow: read transaction returns three lists: pools, `(pool_uid, target)` pairs, and `(pool_uid, buddy_group)` pairs. The handler then appends matching targets/groups to each pool by UID. Missing quota defaults are represented as `-1`.

State and persistence: read-only over pools, entities, targets, buddy groups, and quota default limits.

Dependencies and integration points: used after create/delete/assign pool operations and by management clients. Depends on quota enum SQL values and protobuf response structures.

Risks: merge is quadratic over pool assignments, acceptable for small lists but potentially inefficient at very large scale. Quota limit inclusion uses left joins and sentinel values, so consumers must interpret `-1` as unlimited/unset.

Test signals: async test verifies pool count, assigned target/group counts, and default quota values including `-1` for missing limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_pools.rs -->
