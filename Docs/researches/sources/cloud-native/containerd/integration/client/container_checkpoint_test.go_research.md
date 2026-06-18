# sources/cloud-native/containerd/integration/client/container_checkpoint_test.go

## Purpose
This Linux integration test file validates checkpoint and restore behavior with CRIU, including PTY, runtime/RW/task checkpoints, image-path checkpointing, leave-running checkpoints, and paused tasks.

## Important APIs, Types, and Functions
Tests include `TestCheckpointRestorePTY`, `TestCheckpointRestore`, `TestCheckpointRestoreNewContainer`, `TestCheckpointLeaveRunning`, `TestCheckpointRestoreWithImagePath`, and `TestCheckpointOnPauseStatus`. They use checkpoint/restore opts such as `WithCheckpointRuntime`, `WithCheckpointRW`, `WithCheckpointTaskExit`, `WithCheckpointTask`, `WithRestoreImage`, `WithRestoreSpec`, `WithRestoreRuntime`, `WithRestoreRW`, `WithCheckpointImagePath`, and `WithRestoreImagePath`.

## Control Flow
Each test skips when CRIU is unavailable, creates a client/container/task, starts a process, checkpoints it, deletes or keeps the task depending on scenario, restores a container/task, starts it, verifies behavior through output/status/process listing, then kills and cleans up.

## State and Persistence
Checkpoint images are persisted as containerd images or filesystem CRIU image directories. RW snapshots, runtime state, specs, and image metadata may be stored and restored. Test containers and snapshots are cleaned up.

## Dependencies and Integration Points
Requires Linux, CRIU, runtime checkpoint support, direct IO helpers, client container/task APIs, OCI spec helpers, `cio`, and Unix signals.

## Risks
Highly environment-sensitive: CRIU version, kernel features, runtime support, PTY handling, and process timing affect results. Cleanup must handle paused/running tasks carefully.

## Test Signals
Strong end-to-end coverage for checkpoint/restore with PTY input/output, task exit behavior, restoring to a new container, preserving running state after checkpoint, image-path dump/restore, and checkpointing while paused.
