# sources/distributed-fs/beegfs-go/common/scheduler/scheduler_test.go

Purpose: validates scheduler submission-ID priority encoding/decoding and priority rotation, and benchmarks token distribution.

Important types/tests are `submissionExpectation`, `TestSubmissionIDFunctions`, `TestGetNextPriority`, `BenchmarkDistributeTokensEvenWork`, and `BenchmarkDistributeTokensUnevenWork`.

Control flow: submission tests create IDs from base keys and priorities, decode priority and base key, increment IDs, demote and promote priorities, and verify expected boundaries including max uint64 base-36 rollover. `TestGetNextPriority` confirms rotating cycles start at each priority and each priority appears five times across nested cycles. Benchmarks initialize work-token counters and repeatedly call the distributor for even and skewed queue shapes.

State behavior under test is in-memory ID strings, priority counters, and atomic work token counters. No scheduler goroutine is started in benchmarks; they instantiate `Scheduler{log: zap.NewNop()}` directly.

Dependencies include `testing`, `fmt`, `testify/assert`, and zap.

Integration points are scheduler ID contracts used by queue storage and priority token release.

Risks: tests do not cover `NewScheduler` ticker behavior, moving-average calculations, expvar registration, rescheduled work timing, or invalid malformed submission IDs. Benchmarks exercise performance but do not assert fairness ratios.

Test signals: strong coverage for stable ID encoding contracts, which are critical for persisted queue ordering.
