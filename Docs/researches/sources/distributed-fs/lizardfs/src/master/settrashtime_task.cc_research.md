# sources/distributed-fs/lizardfs/src/master/settrashtime_task.cc

## Purpose

`settrashtime_task.cc` implements `SetTrashtimeTask`, a task-manager-backed operation for changing trash retention time over one or more inodes, optionally recursively. The source was read as a complete 115-line implementation.

## Important APIs, Types, and Functions

Methods are `execute`, `isFinished`, and `setTrashtime`. The task tracks inode list, current iterator, user ID, target trash time, set mode, and shared stats.

## Control Flow

Execution processes one inode, applies `setTrashtime`, queues child tasks for recursive directories, maps non-recursive permission denial to `EPERM`, updates stats, and emits a `SETTRASHTIME` changelog on change. `setTrashtime` supports set, increase, and decrease modes.

## State and Persistence Behavior

When changed, the node trash time and ctime are updated, checksum is recomputed, and trash nodes are reindexed in `gMetadata->trash` under their new `TrashPathKey`. Persistent replay is represented by the emitted changelog.

## Dependencies and Integration Points

Dependencies include filesystem checksum/operations, metadata trash map, node types, `TaskManager`, and protocol set-mode constants. It integrates with recursive metadata operations and trash subsystem indexing.

## Risks and Edge Cases

Stats pointer must be valid for actionable operations. Permission behavior mirrors setgoal. Reindexing trash entries uses `gMetadata->trash.at(old_trash_key)`, so missing old keys would throw or abort depending container behavior. Increase/decrease modes change only if the target moves in the requested direction.

## Test Signals

Tests should cover set/increase/decrease, trash-map rekeying, changed/not-changed/not-permitted stats, recursive traversal, permission failures, and changelog/checksum updates.
