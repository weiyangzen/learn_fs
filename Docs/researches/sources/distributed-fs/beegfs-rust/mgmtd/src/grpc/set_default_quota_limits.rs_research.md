<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_default_quota_limits.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_default_quota_limits.rs

Purpose: updates or clears default quota limits for a storage pool.

Important APIs/types/functions: `set_default_quota_limits()` resolves the pool and applies optional user/group space/inode limit fields. The nested `update()` helper treats `-1` as delete/unlimited, values greater than `-1` as upsert, and values below `-1` as invalid.

Control flow: quota license, pre-shutdown, and `quota_enable` checks run before mutation. The write transaction resolves the pool once, then applies only fields present in the request.

State and persistence: writes or deletes rows in `quota_default_limits` keyed by pool, ID type, and quota type.

Dependencies and integration points: used by management clients and read by `get_pools`, `get_quota_usage`, and quota enforcement calculations.

Risks: the handler does not proactively notify nodes; enforcement changes take effect through the next quota distribution cycle. Sentinel `-1` semantics must remain consistent with readers.

Test signals: no direct tests. Useful tests would cover each field, invalid negative values, deletion, pool resolution, quota disabled, and enforcement interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_default_quota_limits.rs -->
