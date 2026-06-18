# sources/distributed-fs/lizardfs/src/master/snapshot_task.h

## Purpose

`snapshot_task.h` declares `SnapshotTask`, the task-manager-backed implementation of recursive snapshot creation. The source was read as a complete 124-line header.

## Important APIs, Types, and Functions

The class derives from `TaskManager::Task`, defines `SubtaskContainer` as `(inode, name)` pairs, has a constructor with source/destination/options, declares `cloneNode`, `execute`, `isFinished`, `generateDescription`, and protected clone helpers for node testing, existing/new nodes, file chunks, directories, symlinks, and changelog emission.

## Control Flow

The header documents that each clone task handles one inode and may enqueue new tasks for directory children. Constructor assertions enforce either a single subtask with an explicit destination inode or multiple subtasks with destination inode zero.

## State and Persistence Behavior

State includes original inode, destination parent/inode, overwrite and ignore-missing flags, changelog and enqueue-work flags, current subtask iterator, and a local task list. Persistent effects are performed by implementation through filesystem and changelog APIs.

## Dependencies and Integration Points

It depends on `TaskManager`, filesystem nodes, `HString`, and standard containers. It is used by snapshot filesystem operations and metarestore replay.

## Risks and Edge Cases

The class holds raw task pointers in intrusive lists and relies on `TaskManager` cleanup. Callers must choose flags carefully: `emit_changelog_` changes persistence behavior, and `enqueue_work_` determines whether directories are recursively cloned.

## Test Signals

Compile coverage and task-manager tests for recursive snapshots, explicit inode restore snapshots, overwrite handling, and cancellation/cleanup.
