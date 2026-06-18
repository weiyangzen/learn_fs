# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/DirectoryPathWaiterTest.java

## Purpose
Parameterized tests for directory-load path waiters with `DirectoryLoadType.BFS` and `DFS`. It validates release rules for exact path, child path, nested path, parent path, truncated directory loads, and final task completion.

## Important APIs/types/functions
- Parameterized `directoryLoadTypes()` returns BFS and DFS.
- Creates `BaseTask` for `DescendantType.ALL` with the chosen directory load type.
- Uses `waitForSync`, `nextCompleted`, `SyncProcessResult`, `PathSequence`, and `PathLoadTask.onProcessComplete`.

## Control flow
- `TestWaiter` waits on the base path and releases it after a non-truncated root result.
- `TestMultiWaiter` releases a child when its own non-truncated directory result completes but not when truncated.
- `TestNestedWaiter` proves completing an unrelated nested path does not release waiters, while completing the parent releases direct children.
- `TestParentWaiter` shows root completion releases direct child `/path`, `/path` completion releases `/path/nested`, and final task completion releases deeper `/path/nested/1`.

## State and persistence behavior
- In-memory waiter coordination only.
- Truncated results intentionally keep waiters blocked until a full result or task completion.

## Dependencies and integration points
- Uses mocked DefaultFileSystemMaster for journal context and MetadataSyncHandler callback wiring.
- Complements `BatchPathWaiterTest` by exercising directory-load strategies rather than single-listing sorted ranges.

## Risks and edge cases
- Timeout-based future assertions may be environment-sensitive.
- Does not compare BFS vs DFS ordering differences beyond shared waiter release contract.

## Test signals
- Strong signal for metadata sync clients waiting on directory traversal under BFS/DFS load modes.
