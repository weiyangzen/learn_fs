# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/StateLockManagerTest.java

## Purpose
`StateLockManagerTest` verifies master state-lock behavior for timeout grace mode, forced interruption grace mode, exclusive-only startup phase, and reporting of shared waiters/holders.

## Important APIs, Types, and Functions
Tests are `testGraceMode_Timeout()`, `testGraceMode_Forced()`, `testExclusiveOnlyMode()`, and `testGetStateLockSharedWaitersAndHolders()`. The nested `StateLockingThread` acquires shared or exclusive locks and exposes acquisition/interruption state. The tests use `StateLockManager`, `StateLockOptions`, `GraceMode`, `LockResource`, and backup state-lock configuration keys.

## Control Flow, State, and Persistence
Timeout mode starts shared/exclusive holders and expects exclusive acquisition with a short grace period to time out, then verifies success when no holder remains. Forced mode enables interrupt cycles, starts a shared holder, takes the lock exclusively with forced grace, and expects holders/waiters to be interrupted. Exclusive-only mode simulates masters-started callback, verifies shared locks fail during the exclusive-only duration, and exclusive locks still succeed. Waiter/holder reporting starts multiple shared holders and asserts their thread names appear.

## Dependencies and Integration Points
It depends on master state locking used for backups/checkpointing and global configuration. The tests exercise concurrency behavior with real threads.

## Risks and Test Signals
Risks covered include backup exclusive lock starvation, failure to interrupt shared lockers, accidental shared access during exclusive-only startup, and inaccurate lock diagnostics. Signals are deterministic timeouts, interruption flags, and reported shared holder names.
