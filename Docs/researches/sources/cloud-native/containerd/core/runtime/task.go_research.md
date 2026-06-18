<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/task.go -->
# sources/cloud-native/containerd/core/runtime/task.go

## Purpose
Defines the core runtime process and task interfaces and state types used throughout containerd runtime management.

## Important APIs, Types, And Functions
- `TaskInfo` identifies a task by ID, runtime, spec bytes, and namespace.
- `Process` defines common process lifecycle methods: state, kill, resize, close IO, start, and wait.
- `ExecProcess` extends `Process` with `Delete`.
- `Task` extends `Process` with PID, namespace, pause/resume, exec, pids, checkpoint, update, process lookup, and stats.
- `ExecOpts`, `ConsoleSize`, `Status`, `State`, and `ProcessInfo` model runtime data.

## Control Flow
This file is contract-only. Runtime implementations such as v2 shim tasks satisfy these interfaces, while services and monitors consume them polymorphically.

## State And Persistence
No state is stored here. `State` and `ProcessInfo` are snapshots returned by implementations.

## Dependencies And Integration Points
Depends on containerd protobuf `types.Any`. Integrates with runtime services, monitors, shim clients, task managers, and API event generation.

## Risks And Edge Cases
`State.ExitStatus` and `ExitedAt` are meaningful only for stopped states. `ProcessInfo.Info` is platform-specific and requires caller type knowledge. Interface changes have broad compatibility impact.

## Test Signals
No direct test in this subset; runtime v2 tests elsewhere exercise concrete implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/task.go -->
