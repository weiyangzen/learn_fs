<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/monitor.go -->
# sources/cloud-native/containerd/core/runtime/monitor.go

## Purpose
Defines the runtime task monitoring abstraction and simple implementations for no-op and multi-monitor broadcasting.

## Important APIs, Types, And Functions
- `TaskMonitor` has `Monitor(task, labels)` and `Stop(task)`.
- `NewMultiTaskMonitor(monitors...)` returns a `multiTaskMonitor`.
- `NewNoopMonitor()` returns a monitor that ignores all calls.
- `multiTaskMonitor` forwards calls to each monitor and stops on first error.

## Control Flow
Calls to `Monitor` or `Stop` on the multi monitor iterate configured monitors in order. Any error aborts remaining calls and is returned. The noop implementation always returns nil.

## State And Persistence
`multiTaskMonitor` stores the monitor slice. No monitor state is persisted by this file.

## Dependencies And Integration Points
Depends on the `Task` interface from `task.go`. Used by runtime services that attach metrics/health/restart monitors to tasks.

## Risks And Edge Cases
No rollback is attempted when one monitor succeeds and a later monitor fails. Callers must decide whether partial monitoring is acceptable.

## Test Signals
No direct listed tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/monitor.go -->
