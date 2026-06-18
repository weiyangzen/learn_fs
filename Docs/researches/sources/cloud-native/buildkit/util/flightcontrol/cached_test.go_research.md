## sources/cloud-native/buildkit/util/flightcontrol/cached_test.go

Purpose: validates `CachedGroup` cache semantics.

Important tests: `TestCached` confirms distinct keys get distinct values, repeat successful calls bypass `fn`, and default errors do not poison cache. `TestCachedError` sets `CacheError` and verifies the first non-context error is reused, while a deadline/context-cause error does not cache.

Control flow/state: tests use booleans and repeated calls to observe whether callback execution occurs. The cancellation case uses `context.WithTimeoutCause`, waits for the context to be done, then calls with the same key and a callback that should run.

Dependencies/integration: `testify/require`, `pkg/errors`, Go context deadlines. Risks covered: accidental caching of transient cancellation and incorrect `CacheError` behavior. Gaps: no high-concurrency test for cached group itself; underlying concurrency is covered in `flightcontrol_test.go`.
