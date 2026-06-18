# sources/distributed-fs/seaweedfs/weed/filer/posixlock/manager_test.go

## Purpose

`posixlock/manager_test.go` validates the concurrent manager around the pure lock set. It focuses on indexing, cleanup, session reaping, namespace-specific release, GETLK behavior, and mutual exclusion under concurrent flock churn.

## Important APIs, Types, and Functions

Tests use `NewManager`, `TryLock`, `Unlock`, `GetLk`, `ReleasePosixOwner`, `ReleaseSession`, `Renew`, `ReapExpired`, and direct inspection of `byKey`, `bySid`, and `lastSeen`.

## Control Flow

The tests acquire locks on keys, attempt conflicts, unlock ranges, and assert map cleanup. Session reaping tests mark one session stale, one fresh, and one never-renewed, then verify only stale leased locks are removed. The concurrency test runs 16 goroutines repeatedly acquiring a whole-file flock, using atomics to detect simultaneous holders.

## State and Persistence Behavior

All state is in-memory. Some tests directly mutate `lastSeen` to simulate stale heartbeats. No external filer or mount RPCs are involved.

## Dependencies and Integration Points

The tests depend on `runtime.Gosched`, `sync`, atomics, and the manager/set lock algorithm. They validate server-side behavior expected by distributed FUSE lock handling.

## Risks and Edge Cases

Direct inspection of unexported maps couples tests tightly to implementation. The concurrency test is probabilistic but high-iteration enough to catch obvious mutual exclusion errors. Time-based tests use `time.Now` and manual backdating rather than an injected clock.

## Test Signals

Signals include no stale index entries after unlock/reap, flock surviving posix-owner release, session 2 lock surviving session 1 release, only stale leased sessions reaped, and zero overlap count in concurrent flock churn.
