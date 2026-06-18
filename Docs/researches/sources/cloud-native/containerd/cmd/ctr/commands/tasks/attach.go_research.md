<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/attach.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/attach.go

## Purpose
Implements `ctr tasks attach` for attaching local stdio to a running task.

## Important APIs, Types, And Functions
Defines `attachCommand`.

## Control Flow
Loads container/spec, detects terminal mode, sets local console raw for TTY, attaches with `cio.NewAttach`, waits for task exit, forwards resize or signals, deletes task on return, and exits with task status.

## State And Persistence
Attaches to live task IO and deletes the task at the end; local terminal state is temporarily changed.

## Dependencies And Integration Points
containerd client/task APIs, console, cio, signal/resize helpers, cli exit codes.

## Risks And Test Signals
`defer task.Delete` can remove task after attach exit, which is destructive; terminal reset must run on errors. Integration covered. Source size reviewed: 86 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/attach.go -->
