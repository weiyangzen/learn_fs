# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockLockManagerTest.java

## Purpose
`BlockLockManagerTest` exercises read/write lock behavior, session cleanup, lock pool limits, reuse, and concurrency stress for `BlockLockManager`.

## Important APIs, Types, and Functions
Tests cover `acquireBlockLock`, `tryAcquireBlockLock`, `checkLock`, and `cleanupSession`. They verify multiple read locks, write-lock exclusion, failed validation for wrong session/block/no record, max-lock exhaustion, rejection of write lock when same session already holds read/write lock, lock reuse only after all uses close, and a 200-thread stress scenario.

## Control Flow, State, and Persistence
The lock manager state is in memory. Tests use try-with-resources to close locks and mutate configuration for maximum lock count, reloading properties after each test.

## Dependencies and Integration Points
It depends on `BlockLockManager`, `BlockLock`, `BlockLockType`, Alluxio configuration, temporary folder JUnit rule, and concurrency primitives.

## Risks and Test Signals
This is a strong concurrency regression suite. Remaining risks include fairness/starvation, long timeout behavior, cleanup while locks are actively in use, and interactions with actual block-store operations under failure.
