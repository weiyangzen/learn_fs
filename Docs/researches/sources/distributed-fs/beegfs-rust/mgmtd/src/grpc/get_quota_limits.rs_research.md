<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_limits.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_limits.rs

Purpose: streams configured per-user/per-group quota limits with optional ID and pool filters.

Important APIs/types/functions: `get_quota_limits()` returns `RespStream<GetQuotaLimitsResponse>`. It resolves an optional pool, builds SQL filters for user/group min/max/list, and pages through grouped quota-limit rows using `QUOTA_STREAM_PAGE_LIMIT`.

Control flow: license and quota-enable guards run first. The SQL `WHERE` string starts as `FALSE` and appends OR clauses only for requested filters. Streaming repeatedly fetches a page at increasing offset, sends each row as `QuotaInfo`, and stops when the page is short.

State and persistence: read-only over `quota_limits` and `pools_ext`.

Dependencies and integration points: used by management clients; depends on quota license, runtime config, response streaming helper, DB enum conversions, and pool entity resolution.

Risks: dynamic SQL is built from numeric request values and resolved pool ID, not raw strings, but the approach is still fragile. If no filters are provided, `WHERE FALSE` returns no rows. Offset pagination can be expensive on huge tables and can observe changes between pages.

Test signals: no direct tests. Needed coverage includes empty filters, user/group range/list combinations, pool filter, multi-page streaming, and quota disabled/unlicensed paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_limits.rs -->
