## sources/distributed-fs/juicefs/pkg/chunk/prefetch_test.go

Purpose: tests the prefetch scheduler's deduplication and execution behavior.

Important tests: `TestPrefetcher` constructs a prefetcher with a callback that records fetched keys, enqueues repeated and distinct keys, waits for worker processing, and asserts expected fetch counts/order properties.

State and persistence: in-memory synchronization only.

Dependencies and integration points: uses Go testing, sleeps/channels, and `prefetcher.fetch`.

Risks and test signals: protects against duplicate concurrent prefetches and dropped worker execution. Timing-based assertions can be sensitive to scheduler delays.
