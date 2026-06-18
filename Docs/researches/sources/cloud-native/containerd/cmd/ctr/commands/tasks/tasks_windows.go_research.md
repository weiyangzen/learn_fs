<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_windows.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_windows.go

## Purpose
Windows task helper implementations for console resize and process listing.

## Important APIs, Types, And Functions
Defines Windows `HandleConsoleResize` and `TaskPids`.

## Control Flow
Resize support is effectively a no-op/limited helper; process listing adapts Windows process info from task `Pids` for tabular output.

## State And Persistence
Read-only process query except any supported resize RPCs.

## Dependencies And Integration Points
Windows build tag, containerd task APIs, tabwriter.

## Risks And Test Signals
Feature parity differs from Unix; tests are platform/integration dependent. Source size reviewed: 88 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/tasks_windows.go -->
