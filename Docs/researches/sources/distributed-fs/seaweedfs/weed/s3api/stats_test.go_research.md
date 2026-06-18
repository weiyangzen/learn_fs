## sources/distributed-fs/seaweedfs/weed/s3api/stats_test.go

Purpose: tests audit fallback behavior in the S3 handler metrics wrapper.

Important tests: `TestTrackAuditFallbackForDirectWriteHeader` and `TestTrackAuditSkipsFallbackWhenHandlerEmits`.

Control flow: each test wraps a small handler with `track`, captures the request passed to the handler, invokes the wrapper using `httptest`, and checks `s3err.AuditAlreadyLogged`. The first handler only calls `WriteHeader`; the second calls `PostLog` before writing.

State and dependencies: no external persistence. Uses request context mutation from `s3err.EnsureAuditTracking` and the audit flag set by `PostLog`.

Signals and risks: covers a regression where successful handlers bypassing shared response helpers missed audit logs. It also prevents double logging. It does not assert metrics values, labels, or forbidden bucket redaction.
