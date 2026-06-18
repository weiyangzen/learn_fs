# sources/cloud-native/moby/daemon/logger/ring_test.go

Purpose: tests lossy ring logger and message ring behavior.

Important APIs/types/functions: `TestRingLogger`, `TestRingCap`, `TestRingClose`, `TestRingDrain`, and throughput benchmarks with different receiver delays.

Control flow/state/persistence: in-memory fake loggers and messages; concurrency around worker goroutine and close.

Dependencies/integration: validates `NewRingLogger`, `messageRing`, and core logger ownership semantics.

Risks: timing-sensitive because of background goroutine; tests must synchronize to avoid flakes.

Test signals: direct confidence in lossy buffering, overflow policy, close/drain behavior, and performance characteristics.
