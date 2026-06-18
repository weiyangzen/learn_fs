## sources/distributed-fs/juicefs/pkg/chunk/singleflight_test.go

Purpose: verifies `Controller` coalesces concurrent calls and shares returned pages safely.

Important tests: `TestSingleFlight` starts concurrent `Execute`/`TryPiggyback` calls for the same key, checks the underlying function runs once for duplicates, validates returned page data/errors, and exercises non-piggyback behavior when no request is active.

State and persistence: in-memory goroutines, counters, and pages.

Dependencies and integration points: uses Go testing and `Page` reference release semantics.

Risks and test signals: protects the read de-duplication path used by cache misses. Does not cover nil-page error edge cases explicitly.
