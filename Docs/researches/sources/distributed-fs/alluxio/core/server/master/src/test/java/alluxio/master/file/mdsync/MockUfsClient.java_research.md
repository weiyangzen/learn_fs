# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/MockUfsClient.java

## Purpose
Test `UfsClient` implementation for metadata sync task tests. It can return scripted listings, function-generated listings, get-status results, injected errors, and a configurable rate limiter.

## Important APIs/types/functions
- Implements `UfsClient.performListingAsync` and `getRateLimiter`.
- Adds test helper methods `setError`, `setRateLimiter`, `setResult`, `setGetStatusItem`, and `setListingResultFunc`.
- Provides `performGetStatusAsync` helper with the same callback shape used by tests.

## Control flow
- `performGetStatusAsync` returns either empty or singleton `UfsLoadResult` based on fixed or function-derived status.
- `performListingAsync` first injects `mError` if present; otherwise uses `mResultFunc`; otherwise consumes the next scripted stream from `mItems`.
- Listing results are collected, last item becomes continuation/start-after marker, truncation is controlled by function boolean or whether more scripted batches exist.
- `getRateLimiter` returns configured limiter or unlimited zero-rate limiter.

## State and persistence behavior
- Mutable test state controls future callback behavior.
- No asynchronous threads are created here; callbacks are invoked synchronously by the test mock.

## Dependencies and integration points
- Integrates with `TaskTracker`, `BaseTask`, `UfsLoadResult`, `UfsStatus`, `DescendantType`, and rate limiter tests.

## Risks and edge cases
- Function/script listing paths assume non-empty item lists when constructing `lastItem`; empty listing through those paths can throw.
- Fields are package-private and mutable, fitting tests but not thread-safe beyond controlled scenarios.
- `mGetStatusFunc` has no setter in the shown file, so tests would need package access or direct field access to use it.

## Test signals
- Central scaffold for deterministic UFS load success, retry, truncation, concurrency, and failure scenarios.
