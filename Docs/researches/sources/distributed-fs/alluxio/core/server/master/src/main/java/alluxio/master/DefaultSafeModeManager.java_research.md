<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/DefaultSafeModeManager.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/DefaultSafeModeManager.java

## Purpose
Implements master safe mode timing. It keeps the primary master in safe mode until the RPC server has started and a configured worker-connect wait interval has elapsed.

## Important APIs, Types, And Functions
- `notifyPrimaryMasterStarted()` resets the state to safe mode with no worker-wait start time.
- `notifyRpcServerStarted()` records the current clock time and keeps safe mode marked true.
- `isInSafeMode()` lazily checks elapsed time and flips the mark to false after `MASTER_WORKER_CONNECT_WAIT_TIME`.
- `AtomicMarkableReference<Long>` stores both wait-start timestamp and safe-mode boolean.

## Control Flow
On primary start, the master is in safe mode. On RPC server start, the wait timer begins. Each `isInSafeMode` call first checks the mark, then either remains in safe mode if no start time exists or the wait interval has not elapsed, or uses compare-and-set to exit safe mode.

## State And Persistence Behavior
State is in-memory and clock-based only. It is reset on primary startup and does not persist across process restarts.

## Dependencies And Integration Points
Uses `ElapsedTimeClock`, Alluxio configuration, and SLF4J. It integrates with `AlluxioMasterProcess.startMasterComponents` and RPC server startup notifications through the `SafeModeManager` interface.

## Risks And Edge Cases
Safe mode exit is lazy and depends on callers querying `isInSafeMode`. Clock injection supports deterministic tests; production uses elapsed time to reduce wall-clock drift risks.

## Test Signals
Tests should cover initial true state, reset on primary start, timer start on RPC server start, true before wait time, false after wait time, and idempotent false after exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/DefaultSafeModeManager.java -->
