<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/task/task.go -->
# sources/cloud-native/stargz-snapshotter/task/task.go

## Purpose
Coordinates lower-priority background work so it yields to prioritized operations such as mounts/checks.

## Important APIs, Types, And Functions
- `NewBackgroundTaskManager(concurrency, period)` constructs semaphores and condition variables.
- `DoPrioritizedTask` increments the prioritized count and closes a notification channel to cancel active background tasks.
- `DonePrioritizedTask` waits the silence period, decrements the count, and broadcasts.
- `InvokeBackgroundTask(do, timeout)` retries a cancellable background function until it completes without priority interruption.

## Control Flow
Background invocation waits while priority count is positive, acquires a weighted semaphore slot, snapshots the current notification channel, runs the task under a timeout context, cancels/retries if a priority task starts, and exits only after the task completes.

## State And Persistence
All state is in memory: atomic priority count, semaphore occupancy, notification channels, and condition variable waiters.

## Dependencies And Integration Points
Used by layer prefetch/background fetch to avoid competing with foreground lazy reads. Depends on `golang.org/x/sync/semaphore`.

## Risks And Edge Cases
`DonePrioritizedTask` decrements asynchronously after the silence period, so unbalanced calls can permanently block or make counts negative. `Acquire` uses `context.Background` and ignores errors. Background tasks must honor context cancellation.

## Test Signals
Tests cover priority blocking, concurrency limits, cancellation on priority start, resume after priority completion, and sequential task completion.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/task/task.go -->
