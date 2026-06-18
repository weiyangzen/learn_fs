# sources/distributed-fs/lizardfs/src/master/setgoal_task.cc

## Purpose

`setgoal_task.cc` implements `SetGoalTask`, a task-manager-backed recursive operation for changing file/directory storage goals. The source was read as a complete 95-line implementation.

## Important APIs, Types, and Functions

Methods are `execute`, `isFinished`, and `setGoal`. The task tracks a vector of inode IDs, current iterator, user ID, desired goal, set mode, and shared stats array.

## Control Flow

Each `execute` processes one inode, advances the iterator, resolves the node, calls `setGoal`, and, if recursive mode is enabled on a directory, pushes a new task containing its children to the front of the work queue. Non-recursive permission denial returns `EPERM`; otherwise stats are incremented and changed nodes emit a `SETGOAL` changelog entry.

## State and Persistence Behavior

Changing a file calls `fsnodes_changefilegoal`, may enqueue tape copies when tapeservers are available, updates ctime and checksum, and logs the changelog. Directories store the goal on the node. Stats accumulate in a shared array across subtasks.

## Dependencies and Integration Points

Dependencies include filesystem checksum/node/operations, `TaskManager`, protocol status constants, and `matotsserv` outside `METARESTORE`. It integrates storage goal changes with tape archival enqueueing.

## Risks and Edge Cases

The implementation assumes `stats_` is non-null whenever a result other than `kNoAction` is possible. Permission checks honor `EATTR_NOOWNER`, root UID, and owner UID. Only files/directories/trash/reserved nodes are actionable. Tape enqueueing happens for file goal changes and depends on tapeserver availability at execution time.

## Test Signals

Tests should cover changed/not-changed/not-permitted stats, recursive directory traversal, non-recursive permission failure, checksum/ctime/changelog updates, tape enqueueing, and metarestore build behavior without tapeserver integration.
