<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/common.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/common.rs

Purpose: shared constants for quota-related gRPC handlers.

Important APIs/types/functions: `QUOTA_NOT_ENABLED_STR` standardizes the user-facing error when quota RPCs are called while quota support is disabled. `QUOTA_STREAM_PAGE_LIMIT` sets DB page size to 1,000,000 rows. `QUOTA_STREAM_BUF_SIZE` sets response channel buffer size to 100,000.

Control flow: none.

State and persistence: stateless; affects runtime memory/latency tradeoffs for quota streaming.

Dependencies and integration points: used by `get_quota_limits`, `get_quota_usage`, `set_quota_limits`, and `set_default_quota_limits`.

Risks: large page/buffer settings can use significant memory during large quota queries but reduce DB overhead. The values are tuned from local performance comments and may need reassessment on production-scale deployments.

Test signals: no direct tests. Streaming quota tests should cover empty, small, and multi-page result sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/common.rs -->
