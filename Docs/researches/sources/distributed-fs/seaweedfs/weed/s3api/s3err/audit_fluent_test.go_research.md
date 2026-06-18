# sources/distributed-fs/seaweedfs/weed/s3api/s3err/audit_fluent_test.go

Purpose: tests audit log field extraction and duplicate-log tracking.

Important APIs/types: test functions exercise `GetAccessLog`, `EnsureAuditTracking`, `MarkAuditLogged`, and `AuditAlreadyLogged`.

Control flow: tests create `httptest` requests, attach request IDs or identity holders, set forwarding headers, and assert the resulting `AccessLog` fields. The tracking test checks untracked, newly tracked, idempotently tracked, and marked states.

State and persistence behavior: no external fluent logger is used. Tests avoid global `Logger` and focus on pure request-derived state.

Dependencies and integration points: imports S3 constants and request-id context helpers, so it validates integration with authentication/fallback identity flow.

Risks: tests do not cover `InitAuditLog`, fluent posting errors, `PostLog` mark-before-nil semantics, or operation classification across multiple query keys. Remote IP tests intentionally document trusted-header behavior but cannot enforce proxy sanitation.

Test signals: strong unit coverage for recently risky audit correctness: request IDs, identity propagation across request copies, and forwarded IP extraction.
