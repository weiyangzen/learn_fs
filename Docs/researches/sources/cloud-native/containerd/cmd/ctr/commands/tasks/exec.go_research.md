<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/exec.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/exec.go

## Purpose
Implements `ctr tasks exec` for starting an additional process inside a running container.

## Important APIs, Types, And Functions
Defines `execCommand` and `stdinCloser`.

## Control Flow
Validates args, builds process spec options for cwd/env/user/tty/args, creates a new process with IO options, starts it, either detaches or waits while forwarding resize/signals, closes stdin on read EOF, and returns process exit code.

## State And Persistence
Creates live exec process records and FIFO/log IO paths; local console may enter raw mode.

## Dependencies And Integration Points
containerd task/process API, cio, oci process spec helpers, console, signal/resize handling.

## Risks And Test Signals
Exec ID must be unique; detached processes outlive the CLI. Stdin closer behavior is subtle. Covered by integration more than unit tests. Source size reviewed: 209 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/exec.go -->
