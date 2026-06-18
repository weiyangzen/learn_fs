<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_usage.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_usage.rs

Purpose: streams aggregated quota usage joined with effective limits and optional exceeded/pool filters.

Important APIs/types/functions: `get_quota_usage()` returns `RespStream<GetQuotaUsageResponse>`. It builds user/group ID filters, optional pool UID `HAVING`, optional exceeded/not-exceeded filtering, and streams grouped `QuotaInfo` rows.

Control flow: after license/quota-enable checks, the handler builds dynamic `WHERE` and `HAVING` clauses, queries `quota_usage` joined to targets/pools/default/specific limits, aggregates usage by quota ID/type/pool, and sends paged responses. The first streamed response includes `refresh_period_s`; later messages omit it.

State and persistence: read-only over quota usage collected by `quota.rs` timers and quota limit tables.

Dependencies and integration points: management clients use this to inspect quota state. It depends on quota update interval config, pool resolution, streaming helpers, and SQLite aggregation.

Risks: no ID filters means no results. Offset pagination may be slow and inconsistent under concurrent updates. Effective limit logic uses `COALESCE(l.value, d.value, -1)` and exceeded checks require positive limits.

Test signals: no direct tests in this file; quota update tests populate usage. Streaming/filter tests would improve confidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_usage.rs -->
