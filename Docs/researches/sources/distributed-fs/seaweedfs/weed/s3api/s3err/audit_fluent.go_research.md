# sources/distributed-fs/seaweedfs/weed/s3api/s3err/audit_fluent.go

Purpose: S3 access audit logging through fluent-logger, plus per-request audit tracking to avoid duplicate fallback logs. It builds AWS-style access records from HTTP requests and posts them asynchronously when configured.

Important APIs/types: `AccessLog`, `AccessLogHTTP`, and `AccessLogExtend` define audit payloads. `InitAuditLog` loads fluent config. `GetAccessLog` builds a record. `PostLog` and `PostAccessLog` emit records. `EnsureAuditTracking`, `MarkAuditLogged`, and `AuditAlreadyLogged` maintain an atomic per-request flag.

Control flow: `InitAuditLog` reads JSON config into `fluent.Config`, defaults `TagPrefix` from `ENVIRONMENT`, enables async posting, and installs a callback logger. `GetAccessLog` extracts bucket/key, error code, request id, requester identity from context, signature type, host, user-agent, remote IP, and operation name. Operation classification inspects query keys such as `delete`, `tagging`, `lifecycle`, `acl`, and `policy`. `PostLog` marks the request logged before checking whether `Logger` is nil, then posts if configured.

State and persistence behavior: global mutable state includes `Logger`, `hostname`, and `environment`. The per-request audit flag is an `atomic.Bool` stored in request context. Logs are externalized to fluent; no local persistence occurs.

Dependencies and integration points: integrates with `fluent-logger-golang`, SeaweedFS `glog`, S3 constants helpers, identity context helpers, and `request_id`. It is called by S3 response writers and likely middleware fallback paths.

Risks: forwarded headers are trusted as-is; the comment explicitly requires proxy-boundary sanitation to prevent spoofed remote IPs. Global `Logger` can be replaced without synchronization, which is typical for init-time config but risky for dynamic reconfiguration/tests. Operation selection returns on the first query key iteration, and Go map iteration is random; requests with multiple recognized subresources could classify nondeterministically. Marking logged before nil logger intentionally suppresses fallback logs even when fluent is disabled.

Test signals: `audit_fluent_test.go` covers request ID source, remote IP precedence including IPv6 and forwarded headers, identity fallback holder behavior, anonymous requester, and audit tracking idempotence/flag transitions.
