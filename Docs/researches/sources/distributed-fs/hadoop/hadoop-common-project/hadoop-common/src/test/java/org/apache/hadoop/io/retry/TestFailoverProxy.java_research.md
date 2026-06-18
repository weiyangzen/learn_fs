# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestFailoverProxy.java

## Purpose
`TestFailoverProxy` validates dynamic proxy failover behavior when operations fail with ordinary exceptions, standby exceptions, IO exceptions, and remote exceptions.

## Important APIs, Types, and Functions
`FlipFlopProxyProvider<T>` alternates between two implementations and counts failovers. `FailOverOnceOnAnyExceptionPolicy` returns `FAILOVER_AND_RETRY` only before the first failover. Tests use `RetryProxy.create()`, `RetryPolicies.failoverOnNetworkException()`, `UnreliableInterface`, and `UnreliableImplementation.TypeOfExceptionToFailWith`. Nested `SynchronizedUnreliableImplementation` and `ConcurrentMethodThread` coordinate concurrent failure paths with `CountDownLatch`.

## Control Flow
Basic tests call methods that succeed once or ten times and then fail, proving policies either fail over or propagate. Network/standby tests verify failover only happens for standby exceptions or idempotent IO operations. The concurrency test forces two threads to fail on the same active proxy and asserts only one provider failover occurs. The multi-standby test repeatedly flips between two standby services until one implementation changes identifier after a delay.

## State and Persistence
State is in proxy provider active pointer, failover count, unreliable implementation invocation counters, latches, and thread results. No external persistence exists.

## Dependencies and Integration Points
The file integrates with Hadoop retry dynamic proxies, `FailoverProxyProvider`, idempotence annotations from `UnreliableInterface`, `StandbyException`, and retry policies used by HA clients.

## Risks and Edge Cases
Concurrency coverage depends on timing and latch coordination. The multi-standby test sleeps up to 10 seconds and depends on retry policy delay behavior. Non-idempotent IO failures must not be retried across failover because the operation may have side effects.

## Test Signals
Signals include expected active implementation strings, propagated exception messages when no failover should occur, exactly one failover under concurrent failures, eventual success after standby recovery, and IO exception propagation for expected non-failover cases.
