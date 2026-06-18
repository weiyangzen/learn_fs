# sources/cloud-native/containerd/plugins/restart/change.go

## Purpose
Defines restart monitor actions for stopping and starting containers to reconcile desired restart state.

## Important APIs, Types, And Functions
`stopChange.apply` kills/deletes an existing task. `startChange.apply` updates restart count labels, creates a new task with configured logging, and starts it. `killTask` kills and deletes an existing task if present.

## Control Flow
Start change loads the OCI spec to determine TTY logging, parses log URI when configured, updates restart count label, kills any existing task, creates a new task with selected `cio` logging, and starts it. `killTask` waits on the task, sends SIGKILL with kill-all, waits for exit, and deletes the task, tolerating some delete-after-error cases.

## State And Persistence
Updates container labels for restart counts and mutates task runtime state by killing/deleting/creating tasks. It does not change restart policy labels.

## Dependencies And Integration Points
Uses containerd client container/task APIs, restart labels, `cio` logging helpers, URL parsing, and syscall signals. Called from `monitor.go`.

## Risks
Force-killing tasks is disruptive but intentional for reconciliation. If task status/wait/delete behavior differs by runtime, errors may leave tasks partially cleaned. Unsupported legacy logpath is handled in monitor, not here.

## Test Signals
No direct tests in this subset.
