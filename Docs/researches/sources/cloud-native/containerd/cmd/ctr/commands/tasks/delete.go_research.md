<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/delete.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/delete.go

## Purpose
Deletes tasks or individual exec processes and reports their exit status.

## Important APIs, Types, And Functions
Defines `deleteCommand` and `loadTask`.

## Control Flow
Builds delete options from `--force`, then either loads a named exec process and deletes it or iterates containers, loads tasks, deletes them, prints exit status/PID/time, and returns the last error.

## State And Persistence
Mutates live task/process state; forced delete sends kill before removal.

## Dependencies And Integration Points
containerd client process/task deletion APIs, cio namespace for loading tasks, log output.

## Risks And Test Signals
Partial failures across multiple containers are possible; force is destructive. Integration tests usually cover task lifecycle. Source size reviewed: 113 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/delete.go -->
