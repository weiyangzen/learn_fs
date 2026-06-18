# sources/distributed-fs/alluxio/core/server/worker/src/test/java/com/google/common/util/concurrent/MockRateLimiter.java

Purpose: Guava-package test helper that provides a deterministic `RateLimiter` with a fake clock and observable sleep events.

Important APIs and helpers: constructor creates `RateLimiter.create(permitsPerSecond, mTicker)`. `getGuavaRateLimiter()` exposes the real Guava limiter. `sleepMillis(int)` advances user time. `readEventsAndClear()` returns and clears recorded events. Nested `FakeSleepingTicker` extends `RateLimiter.SleepingStopwatch`.

Control flow and state: `readMicros()` returns fake time. User sleeps record `U<seconds>` events; rate-limiter sleeps record `R<seconds>` events through `sleepMicrosUninterruptibly`. Each sleep advances the fake microsecond counter.

Dependencies and integration: intentionally lives in `com.google.common.util.concurrent` because older Guava made `SleepingStopwatch` package-private. Uses `MILLISECONDS`, `Locale.ROOT`, and event lists.

Risks and test signals: package placement couples tests to Guava internals and version behavior. It is useful for deterministic throttling tests without wall-clock sleeps.
