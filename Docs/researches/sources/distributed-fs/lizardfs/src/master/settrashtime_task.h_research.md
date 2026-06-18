# sources/distributed-fs/lizardfs/src/master/settrashtime_task.h

## Purpose

`settrashtime_task.h` declares `SetTrashtimeTask`, the task abstraction for recursive trash-time changes. The source was read as a complete 82-line header.

## Important APIs, Types, and Functions

The class defines result counters and `StatsArray`, constructors for batched and direct usage, `execute`, `isFinished`, `generateDescription`, and `setTrashtime`. It stores inode iteration state, UID, trash time, set mode, and stats.

## Control Flow

The header defines the one-task-per-batch model; the implementation advances the current iterator and can enqueue child work.

## State and Persistence Behavior

Only in-memory task state is stored here. Metadata mutation and changelog persistence are in the implementation.

## Dependencies and Integration Points

It includes filesystem node and task manager types and is used by filesystem operations that change retention settings.

## Risks and Edge Cases

The batch constructor asserts non-empty input; the direct constructor leaves the inode vector empty and should not be used with `execute` without setup.

## Test Signals

Compile coverage and filesystem operation tests for set/increase/decrease trash-time changes.
