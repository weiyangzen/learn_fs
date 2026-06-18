# sources/distributed-fs/lizardfs/src/master/recursive_remove_task.cc

## Purpose

`recursive_remove_task.cc` implements `RemoveTask`, a `TaskManager::Task` that removes directory trees incrementally by enqueueing child-removal subtasks before unlinking non-empty directories. The source was read as a complete 84-line implementation.

## Important APIs, Types, and Functions

Methods are `isFinished`, `retrieveNodes`, `doUnlink`, and `execute`. The task stores subtask names, parent inode, `FsContext`, and a repeat counter to detect directories that are continuously repopulated.

## Control Flow

`execute` resolves the parent directory and current child, validates write and sticky permissions, then either enqueues a new `RemoveTask` for a non-empty child directory or unlinks the current child. Directory children are pushed to the front of the shared work queue so a depth-first removal sequence empties directories before the parent advances. After too many repeats on the same directory, it returns `ENOTEMPTY`.

## State and Persistence Behavior

Each successful unlink emits an `UNLINK` changelog entry, updates filesystem stats, and calls `fsnodes_unlink`, which mutates in-memory metadata and downstream persistence via changelog. Task progress is the current iterator and repeat counter.

## Dependencies and Integration Points

It depends on filesystem node lookup, access checks, sticky access, changelog emission, stats, `FsContext`, `HString`, and `TaskManager`. It is used by recursive remove operations that cannot complete in one event-loop tick.

## Risks and Edge Cases

If the parent disappears, permissions change, or child disappears, the task fails. Concurrent creation inside a deleting directory can hit the repeat counter. The code static-casts parent to directory after lookup/access, relying on callers to pass directory parents. Recursive work is generated from a snapshot of current entries.

## Test Signals

Tests should cover recursive non-empty directories, permission/sticky failures, missing parent/child, repeated repopulation causing `ENOTEMPTY`, changelog ordering, and cancellation through `TaskManager`.
