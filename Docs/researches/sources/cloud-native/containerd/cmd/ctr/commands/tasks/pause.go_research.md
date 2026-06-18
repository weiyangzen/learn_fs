<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/pause.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/pause.go

## Purpose
Pauses a running task.

## Important APIs, Types, And Functions
Defines `pauseCommand`.

## Control Flow
Loads the named container and task, then calls `task.Pause`.

## State And Persistence
Mutates task runtime state to paused.

## Dependencies And Integration Points
containerd client task API.

## Risks And Test Signals
Runtime must support pause; no fallback. Integration tested through task lifecycle. Source size reviewed: 44 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/pause.go -->
