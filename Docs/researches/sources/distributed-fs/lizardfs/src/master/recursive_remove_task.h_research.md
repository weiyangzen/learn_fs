# sources/distributed-fs/lizardfs/src/master/recursive_remove_task.h

## Purpose

`recursive_remove_task.h` declares `RemoveTask`, the task-manager-backed implementation of recursive deletion. The source was read as a complete 85-line header.

## Important APIs, Types, and Functions

`RemoveTask` derives from `TaskManager::Task`, defines `SubtaskContainer` as a vector of `HString`, has a constructor taking subtasks, parent inode, and `FsContext`, overrides `execute` and `isFinished`, and provides `generateDescription`. Private helpers are `retrieveNodes` and `doUnlink`; state includes `kMaxRepeatCounter`.

## Control Flow

The header describes the task model: one task handles one node/name at a time, adds children to the front of the queue for non-empty directories, and removes itself from the queue once its subtask iterator finishes.

## State and Persistence Behavior

State is per-task in memory. Persistent filesystem effects are performed by the implementation through changelog and node operations.

## Dependencies and Integration Points

It includes special inode definitions, filesystem node/operations, `HString`, `FsContext`, and `TaskManager`, making it part of asynchronous filesystem operation handling.

## Risks and Edge Cases

The constructor initializes `current_subtask_` from the moved vector; callers must pass a non-empty meaningful subtask list. The task retains a shared context, so context lifetime is shared with background processing.

## Test Signals

Compile coverage and filesystem operation tests that submit `RemoveTask` through `TaskManager` with recursive and permission-sensitive cases.
