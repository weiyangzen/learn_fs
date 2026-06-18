<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/request_exceeded_quota.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/request_exceeded_quota.rs

**Purpose:** Calculates quota IDs exceeding effective limits for a target or storage pool.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `RequestExceededQuota`, response `RequestExceededQuotaResp`, error response with `OpsErr::INTERNAL` and default `SetExceededQuota`. Uses `LicensedFeature::Quota` and SQL over `quota_usage`, `targets`, `quota_default_limits`, and `quota_limits`.

**Control flow:** Verifies quota feature licensing, resolves pool ID directly from the message or by looking up the target's pool, queries distinct quota IDs grouped by id type/quota type/pool where summed usage exceeds explicit or default limit, and returns `SUCCESS` plus `SetExceededQuota`.

**State and persistence behavior:** Read-only. It exposes current quota calculation state to storage nodes for enforcement.

**Dependencies and integration points:** Integrates quota licensing, quota usage collection, default/explicit limit tables, and classic quota enforcement messages.

**Risks:** If `pool_id` is zero and target lookup fails, the handler errors. SQL comparison with null limits depends on data integrity; missing limits may not flag exceeded IDs. The response preserves the original `pool_id`, so target-derived pool responses can have `pool_id=0` in `inner`.

**Test signals:** Existing tests cover user/group, space/inode, direct pool, target-derived pool, and empty results. Add license-denied tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/request_exceeded_quota.rs -->
