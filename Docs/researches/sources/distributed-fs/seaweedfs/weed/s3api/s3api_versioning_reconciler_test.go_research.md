<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler_test.go

Purpose: tests queue mechanics for the versioning reconciler and retry semantics for filer operations used by version pointer updates.

Important APIs/functions: tests cover `newVersionsHealQueue`, `Enqueue`, `Len`, `popReady`, `requeue`, `versionsHealMaxRetries`, and `retryFilerOp` with transient, exhausted, canceled, and terminal errors.

Control flow: queue tests enqueue duplicates, overfill capacity, inject delayed candidates, requeue with backoff, and assert give-up drops max-attempt candidates. Retry tests use closures counting calls and validate success before exhaustion, wrapped exhaustion errors, context cancellation interrupting sleep, and short-circuiting NotFound/canceled/deadline errors.

State and persistence behavior: no persistent state. Queue tests mutate in-memory pending maps; retry tests do not access a filer.

Dependencies and integration: uses context, filer not-found sentinel, gRPC status/codes, testify, and retry constants defined elsewhere in versioning object logic. It complements `s3api_versioning_reconciler.go`.

Risks: tests access queue internals directly for deferred candidates, so internal representation changes require updates. `retryFilerOp` is not defined in the reconciler file but is part of the same versioning repair behavior; failures here indicate broader update-latest retry regressions.

Test signals: passing tests mean heal queue growth is bounded/deduplicated, retries honor backoff and caps, shutdown/client cancellation can interrupt retry sleep, and terminal errors are not retried or wrapped as exhausted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_versioning_reconciler_test.go -->
