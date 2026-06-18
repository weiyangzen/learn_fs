<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_quota_limits.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_quota_limits.rs

Purpose: updates or clears specific quota limits for user/group IDs across pools.

Important APIs/types/functions: `set_quota_limits()` iterates request `limits`, resolves each pool, converts ID type, and applies optional space/inode limits using prepared `REPLACE` and `DELETE` statements.

Control flow: quota license, pre-shutdown, and `quota_enable` checks gate the write transaction. For each quota entry, values greater than `-1` are persisted; `-1` or lower deletes the row for that quota type. Missing fields are left unchanged.

State and persistence: mutates `quota_limits` rows keyed by quota ID, ID type, quota type, and pool ID.

Dependencies and integration points: read by quota usage RPC and quota enforcement. Relies on pool entity resolution and quota enum SQL variants.

Risks: unlike default limits, values below `-1` are treated as delete rather than invalid, which may be inconsistent. Per-entry pool resolution can be repetitive for large batches. Enforcement waits for periodic distribution.

Test signals: no direct tests. Needed coverage includes mixed insert/delete, invalid/missing quota IDs, repeated pools, quota disabled, and value semantics below `-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_quota_limits.rs -->
