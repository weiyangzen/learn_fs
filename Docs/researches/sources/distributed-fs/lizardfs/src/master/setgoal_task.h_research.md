# sources/distributed-fs/lizardfs/src/master/setgoal_task.h

## Purpose

`setgoal_task.h` declares `SetGoalTask`, the task abstraction for potentially recursive goal changes. The source was read as a complete 83-line header.

## Important APIs, Types, and Functions

The class derives from `TaskManager::Task`, defines result counters `kChanged`, `kNotChanged`, `kNotPermitted`, `kStatsSize`, and `kNoAction`, exposes `StatsArray`, constructors for batch and single-node style use, `execute`, `isFinished`, `generateDescription`, and `setGoal`.

## Control Flow

The header establishes one-inode-at-a-time task execution with optional generation of child tasks from the implementation.

## State and Persistence Behavior

State is held per task and shared stats pointer. Persistent metadata changes are performed by implementation methods.

## Dependencies and Integration Points

It depends on `TaskManager` and filesystem node definitions and is used by filesystem APIs implementing setgoal requests.

## Risks and Edge Cases

The batch constructor asserts a non-empty inode list. The alternate constructor leaves `inode_list_` empty and is suitable only for direct `setGoal`-style use unless initialized before `execute`.

## Test Signals

Compile coverage plus task-manager integration tests for recursive goal changes and direct `setGoal` behavior.
