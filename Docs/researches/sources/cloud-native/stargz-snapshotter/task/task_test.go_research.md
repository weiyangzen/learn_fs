<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/task/task_test.go -->
# sources/cloud-native/stargz-snapshotter/task/task_test.go

## Purpose
Verifies `BackgroundTaskManager` scheduling, cancellation, concurrency, and retry behavior.

## Important APIs, Types, And Functions
- `TestBackgroundTasks` table drives scenarios named `privilege_running`, `concurrency`, `cancel`, `resume`, `finish_partial`, and `finish_all`.
- `sampleTask` records started/done/canceled flags and blocks on either finish channel or context cancellation.
- Helpers `doGo` and `wait` coordinate goroutine startup and polling assertions.

## Control Flow
Each test creates a manager and four sample tasks, runs a scenario that invokes background work and priority transitions, then checks final task flags. Timeout polling fails after five seconds.

## State And Persistence
All state is in-memory task flags, channels, and manager counters. No files are written.

## Dependencies And Integration Points
Directly tests `task.go` and indirectly validates assumptions used by layer prefetch/background fetch code.

## Risks And Edge Cases
Timing sleeps make tests sensitive to slow CI, though waits use generous timeouts. The test names use `privilege` where the implementation says prioritized, but behavior is clear.

## Test Signals
Passing means background tasks do not start during priority work, concurrency is capped, running tasks are canceled when priority starts, tasks resume after silence, and semaphore slots are released after completion.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/task/task_test.go -->
