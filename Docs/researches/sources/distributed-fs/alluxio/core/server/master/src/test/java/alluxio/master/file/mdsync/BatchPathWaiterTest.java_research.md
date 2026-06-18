# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/BatchPathWaiterTest.java

## Purpose
Tests `BatchPathWaiter` behavior used by single-listing metadata sync tasks. It verifies when waiters on paths are released as sorted/truncated UFS batches complete, including in-order, out-of-order, and final task completion cases.

## Important APIs/types/functions
- Creates `BaseTask` with `DirectoryLoadType.SINGLE_LISTING`; casts root tasks to `BatchPathWaiter` for completed range assertions.
- Uses `SyncProcessResult` and `PathSequence` to feed completed path intervals to `nextCompleted`.
- Mocks `MetadataSyncHandler.onPathLoadComplete` to call `path.onComplete`.
- Uses executor futures around `waitForSync`.

## Control flow
- Waiter tests submit blocking waits, call `nextCompleted` with partial/final batches, assert timeout or release, and finally call `getPathLoadTask().onProcessComplete`.
- In-order and out-of-order tests inspect `getLastCompleted()` range merging, proving contiguous intervals collapse and disjoint intervals remain separate.
- Single path task completion verifies `isCompleted` becomes present only after process completion.

## State and persistence behavior
- State under test is in-memory completed path ranges and waiter queues.
- Final task completion releases remaining waiters even when their path was not passed by a non-truncated completed range.

## Dependencies and integration points
- Integrates BaseTask, PathLoadTask completion callbacks, MetadataSyncHandler, and DefaultFileSystemMaster journal context stubbing.

## Risks and edge cases
- Timeout-based assertions can be slow/flaky under heavy load.
- Test method `TestBaseTackSinglePath` has a typo in the name only.
- Range comparison depends on lexical path ordering.

## Test signals
- Strong signal for concurrent metadata sync wait semantics and completed-range merging.
- Regression indicators: waiters released on truncated batches, not released on final completion, or completed intervals merging incorrectly.
