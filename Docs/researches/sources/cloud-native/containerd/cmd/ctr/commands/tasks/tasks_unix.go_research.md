<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_unix.go

## Purpose
Unix task helper implementations for console resize and process listing.

## Important APIs, Types, And Functions
Defines Unix `HandleConsoleResize` and `TaskPids` helpers.

## Control Flow
Resize registers SIGWINCH and sends current terminal size to task pty. Process listing calls task `Pids` and prints OS process IDs plus info.

## State And Persistence
Process-local signal watch; reads live task process state; sends resize RPCs.

## Dependencies And Integration Points
console, syscall, containerd task APIs, tabwriter.

## Risks And Test Signals
Resize goroutine must stop with context; process info formatting depends on runtime payloads. Indirect integration coverage. Source size reviewed: 129 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_unix.go -->
