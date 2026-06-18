# sources/distributed-fs/lizardfs/src/mount/global_io_limiter_unittest.cc

## Purpose
This file tests the timing and concurrency behavior of mount I/O limiting. Many tests are integration-style because limiter correctness depends on clocks, groups, proxy logic, and token database behavior interacting.

## Important APIs, Types, And Functions
`TestingLimiter` exposes `callReconfigure()`. `UnlimitedLimiter` grants every request. `ManuallyAdjustedClock` blocks sleepers until manually advanced and aborts on timeout to catch hangs. `FastClock` jumps directly to requested sleep times. `IoLimitsDatabaseLimiter` wraps `IoLimitsDatabase` and counts request calls. Tests cover `Group::wait()`, `Group::die()`, `LimiterProxy::waitForRead()`, and shared throughput across multiple proxies.

## Control Flow
Simple tests check immediate deadline timeout and no sleeping when unlimited. Future-based tests launch many async operations, reconfigure limits, advance manual clocks, and assert exactly how many operations complete per tick. The exact-time test computes expected microseconds from bytes, delta, and throughput. Multi-mount tests verify several `LimiterProxy` instances share one underlying limiter. Request-count tests ensure the proxy aggregates waits and does not call the limiter excessively.

## State And Persistence
State is test-local: clocks, databases, groups, proxies, futures, atomics, condition variables, and counters. There is no persistence.

## Dependencies And Integration Points
It depends on GoogleTest, `<future>`, protocol constants, common I/O limiting classes, `IoLimitsDatabase`, and unit-test packet helpers. It validates behavior implemented across `global_io_limiter.*` and common limiter primitives.

## Risks And Test Signals
These tests are sensitive to async scheduling and use abort-based deadlock detection. They strongly signal expected limiter semantics: deadline handling, no unnecessary sleeps, dead-group cancellation, reconfiguration wakeups, aggregate throughput fairness, and bounded master communication. Missing cgroup mocks leave group-removal-through-classification behavior less directly tested.
