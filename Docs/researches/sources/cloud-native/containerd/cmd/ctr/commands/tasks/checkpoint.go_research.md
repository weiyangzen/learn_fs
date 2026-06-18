<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/checkpoint.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/tasks/checkpoint.go

## Purpose
Implements task checkpointing with CRIU/runc-specific options.

## Important APIs, Types, And Functions
Defines `checkpointCommand` and `withCheckpointOpts`.

## Control Flow
Validates container ID, opens client with selected runtime default, loads task and container info, attaches checkpoint options for exit/image/work paths, calls `task.Checkpoint`, and prints checkpoint name unless an image path was requested.

## State And Persistence
Creates checkpoint image/content or external CRIU image/work files; may stop the task with `--exit`.

## Dependencies And Integration Points
containerd checkpoint API and runc checkpoint options type.

## Risks And Test Signals
Options are documented as suitable only for runc; type assertion ignores non-runc option mismatch. Tested by contrib checkpoint scripts rather than unit tests. Source size reviewed: 104 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/tasks/checkpoint.go -->
