# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/jitter_test.go

Purpose: tests equal-jitter backoff helper used by daily-run dispatch retries.

Important APIs/types: `TestJitterBounds`, `TestJitterZeroAndNegative`, and `TestJitterTinyDuration` exercise `jitter`.

Control flow: repeated calls assert jitter is in `[d/2, d)` for normal durations, zero for zero/negative durations, and unchanged for 1ns to avoid `rand.Int63n(0)`.

State and persistence behavior: none.

Dependencies and integration points: validates retry timing helper from `dispatch.go`.

Risks: random tests can theoretically flake only if implementation violates bounds; they do not assert distribution quality or seeding.

Test signals: useful edge-case guard for retry backoff panics and thundering-herd mitigation bounds.
