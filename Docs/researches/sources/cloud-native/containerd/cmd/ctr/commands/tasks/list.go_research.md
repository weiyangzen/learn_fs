<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/list.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/list.go

## Purpose
Lists containerd tasks from the task service.

## Important APIs, Types, And Functions
Defines `listCommand`.

## Control Flow
Calls `TaskService().List`, then prints either IDs only or a tabular task/PID/status view.

## State And Persistence
Read-only daemon query; stdout only.

## Dependencies And Integration Points
Task service API and tabwriter.

## Risks And Test Signals
No filters; output reflects task service state only. Simple CLI behavior with integration coverage. Source size reviewed: 72 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/list.go -->
