# sources/cloud-native/moby/daemon/checkpoint.go

## Purpose
Implements create, delete, and list operations for container checkpoints backed by CRIU/runtime task support.

## Important APIs, Types, And Functions
Defines checkpoint name validation variables, helper `getCheckpointDir`, and daemon methods `CheckpointCreate`, `CheckpointDelete`, and `CheckpointList`.

## Control Flow
`getCheckpointDir` selects user-provided or container checkpoint root, checks existence, creates directories on create, and rejects missing/non-directory paths as appropriate. Create resolves the container, obtains a running task under lock, validates the checkpoint ID, creates the directory, calls `CreateCheckpoint`, cleans up on failure, and logs an event. Delete resolves and removes the checkpoint directory. List ensures the root exists and returns directory names.

## State And Persistence
Checkpoint state is persisted as directories under the container checkpoint root or requested external directory. Create uses `0700`; list creates root with `0755`; delete removes recursively.

## Dependencies And Integration Points
Uses daemon container/task APIs, CRIU/runtime checkpoint implementation, backend checkpoint option types, Docker events, and restricted name validation.

## Risks And Test Signals
`filepath.Join(checkpointDir, "")` is used for list root checks. Directory cleanup after failed checkpoint can remove partial runtime output. No direct tests here; integration should cover validation, duplicate names, external dirs, and runtime failures.
