<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/start.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/start.go

## Purpose
Starts an existing created task and optionally waits attached to its exit.

## Important APIs, Types, And Functions
Defines `startCommand`.

## Control Flow
Loads container/task, starts it, prints PID, returns immediately when detached, otherwise waits, handles TTY resize or signal forwarding, and exits with task status.

## State And Persistence
Mutates live task state by starting it; may alter local terminal mode.

## Dependencies And Integration Points
containerd task API, console, cio attach conventions, signal/resize helpers.

## Risks And Test Signals
Start on already running tasks errors; terminal state handling is critical. Integration tested. Source size reviewed: 145 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/start.go -->
