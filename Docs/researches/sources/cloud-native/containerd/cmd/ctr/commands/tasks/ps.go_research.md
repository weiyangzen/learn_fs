<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/ps.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/ps.go

## Purpose
Lists processes within a task.

## Important APIs, Types, And Functions
Defines `psCommand`.

## Control Flow
Loads task, calls platform `TaskPids`, and prints process IDs and info in a table.

## State And Persistence
Read-only live task query.

## Dependencies And Integration Points
containerd task API and platform-specific process enumeration.

## Risks And Test Signals
Process info shape differs by platform. Covered by platform helpers/integration. Source size reviewed: 72 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/ps.go -->
