# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RateLimitingFactory.java

## Purpose
`RateLimitingFactory` is the only Hadoop common utility class that imports the shaded Guava `RateLimiter`, hiding that dependency behind the `RateLimiting` interface.

## Important APIs, Types, And Functions
Public APIs are `unlimitedRate()` and `create(int capacity)`. Internal implementations are `NoRateLimiting` and `RestrictedRateLimiting`. `INSTANTLY` is the shared zero-duration result.

## Control Flow
`create(0)` returns the singleton unlimited limiter. Other capacities create a `RateLimiter` at the requested permits per second. `RestrictedRateLimiting.acquire` calls Guava `acquire(requestedCapacity)`, receives seconds as a double, and converts to milliseconds in a `Duration`, returning the shared zero duration for no delay.

## State And Persistence
The unlimited limiter has no mutable state. Restricted instances hold Guava limiter state in memory. Nothing is persisted.

## Dependencies And Integration Points
It depends on shaded Guava, `Duration`, Hadoop annotations, and `RateLimiting`. It integrates with callers that need throttling without direct Guava API exposure.

## Risks
Negative capacity is passed to `RateLimiter.create` and will fail there. Wait time is truncated to milliseconds, losing submillisecond precision. `capacity == 0` means unlimited, not blocked. Requested capacity validation is delegated to Guava.

## Test Signals
Tests should verify singleton unlimited behavior, zero-duration no-op acquisitions, restricted acquisition delay and duration conversion, invalid capacity handling, and that no other common code imports Guava `RateLimiter` directly.
