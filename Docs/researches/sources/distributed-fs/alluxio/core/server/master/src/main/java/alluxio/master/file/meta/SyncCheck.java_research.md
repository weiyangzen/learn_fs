# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SyncCheck.java

## Purpose
`SyncCheck` is the value returned by `UfsSyncPathCache` to say whether a metadata sync should run and, when skipped, what previous sync time justified the skip. It also creates `SyncResult` objects used to feed sync outcomes back into the cache.

## Important APIs, Types, and Functions
Static values `SHOULD_NOT_SYNC` and `SHOULD_SYNC` represent decisions without a last-sync time. `shouldSyncWithTime(long)` and `shouldNotSyncWithTime(long)` create decisions carrying a timestamp. `isShouldSync()`, `getLastSyncTime()`, `syncSuccess()`, and `skippedSync()` expose decision and result state. Nested `SyncResult` has `INVALID_RESULT`, success/skipped constructors, `isResultValid()`, `wasSyncPerformed()`, and `getLastSyncTime()`.

## Control Flow, State, and Persistence
The class is immutable and not directly persisted. `getLastSyncTime()` is valid only when a real timestamp was supplied. `syncSuccess()` returns a valid performed-sync result with no last-sync timestamp. `skippedSync()` returns a valid non-performed result carrying the decision's last-sync time. `INVALID_RESULT` represents external sync failure and should not update cache validation time.

## Dependencies and Integration Points
`LockingScheme` stores a `SyncCheck` and upgrades locking if `isShouldSync()` is true. `UfsSyncPathCache` computes these objects and consumes `SyncResult` values after metadata sync attempts.

## Risks
Calling `getLastSyncTime()` on `SHOULD_SYNC`, `SHOULD_NOT_SYNC`, or performed-success results throws due to preconditions. Callers must distinguish skipped-sync results from performed-sync results. The typo in the comment does not affect behavior but indicates this class is lightweight rather than a rich state machine.

## Test Signals
Tests should verify valid/invalid timestamp access, result validity flags, performed-versus-skipped flags, skipped result timestamp propagation, and `LockingScheme` behavior when given each decision type.
