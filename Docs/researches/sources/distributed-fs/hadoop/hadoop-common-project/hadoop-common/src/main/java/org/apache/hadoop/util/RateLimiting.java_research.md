# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RateLimiting.java

## Purpose
`RateLimiting` is Hadoop's minimal private abstraction for acquiring capacity from a rate limiter while reporting the time spent waiting as a `Duration`.

## Important APIs, Types, And Functions
The interface declares `Duration acquire(int requestedCapacity)`.

## Control Flow
There is no implementation in this file. The contract allows an implementation to grant a request even when capacity is not currently available and make a subsequent request block until capacity refills, matching Guava `RateLimiter` behavior.

## State And Persistence
The interface owns no state. Implementations maintain token-bucket or no-op state.

## Dependencies And Integration Points
It depends on `java.time.Duration` and Hadoop annotations. `RateLimitingFactory` provides the built-in unlimited and Guava-backed implementations. Object-store and throttling code can depend on this interface without importing Guava directly.

## Risks
The interface does not define validation for zero or negative requested capacity, fairness, interrupt handling, or whether returned duration is exact or rounded. Callers must understand implementation semantics.

## Test Signals
Tests should be implementation-focused: no-op returns zero duration, restricted limiters delay as expected, invalid capacity behavior is documented, and call sites account for returned wait durations.
