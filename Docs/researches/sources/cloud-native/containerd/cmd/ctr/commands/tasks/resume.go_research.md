<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/resume.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/resume.go

## Purpose
Resumes a paused task.

## Important APIs, Types, And Functions
Defines `resumeCommand`.

## Control Flow
Loads the named container and task, then calls `task.Resume`.

## State And Persistence
Mutates task runtime state from paused toward running.

## Dependencies And Integration Points
containerd client task API.

## Risks And Test Signals
Runtime must support resume and task must be paused. Integration covered. Source size reviewed: 44 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/resume.go -->
