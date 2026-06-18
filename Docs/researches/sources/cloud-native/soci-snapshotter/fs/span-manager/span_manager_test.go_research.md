# sources/cloud-native/soci-snapshotter/fs/span-manager/span_manager_test.go

Purpose: validates span-manager construction, span content reconstruction, cache reads, state transitions, and retry behavior using generated gzip zTOCs and synthetic failing readers.

Important APIs and flow: `TestSpanManager` builds tar entries with one or many spans and checks that `GetContents` reconstructs file data. It mutates zTOCs or readers to trigger incorrect max span ID, non-monotonic checkpoints, bad gzip header, and bad span digest errors. `TestSpanManagerCache` resolves a span and then reads offset slices from cache. `TestStateTransition` validates background fetch moves spans to `fetched` and on-demand fetch moves them to `uncompressed`. `TestValidateState` enumerates valid and invalid state transitions. `TestSpanManagerRetries` uses `retryableReaderAt` to corrupt bytes a controlled number of times and assert retry counts.

State and persistence: uses in-memory blob cache and generated zTOC readers. It mutates zTOC checkpoint bytes for corruption tests and mutates read buffers in a fake `ReadAt`.

Dependencies and integration: depends on `ztoc.BuildZtocReader`, `cache.NewMemoryCache`, `testutil.NewTestRand`, gzip, and package-private span manager helpers. It tests internal implementation behavior, not just exported APIs.

Risks and test signals: strong signal for digest verification, offset monotonicity, state machine constraints, and retry semantics. It does not stress high-concurrency `GetContents` races or persistent filesystem cache behavior.
