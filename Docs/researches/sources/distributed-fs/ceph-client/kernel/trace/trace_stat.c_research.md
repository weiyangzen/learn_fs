# sources/distributed-fs/ceph-client/kernel/trace/trace_stat.c

## Purpose

`trace_stat.c` provides tracefs infrastructure for one-shot tracer statistics. A tracer registers `struct tracer_stat`, and this file creates `trace_stat/<name>` that snapshots, sorts, and displays current statistic entries on each open. The complete 358-line file was read.

## Important APIs, Types, and Functions

Public APIs are `register_stat_tracer()` and `unregister_stat_tracer()`. Internal types are `struct stat_node` and `struct stat_session`. Helpers include reset/destroy, rb-tree insertion, `dummy_cmp()`, `stat_seq_init()`, seq operations, open/release handlers, and tracefs file initialization.

## Control Flow

Registration validates callbacks, rejects duplicate pointers, allocates a session, creates the `trace_stat` directory if needed, creates a tracefs file, and links the session globally. Opening checks lockdown, clears old data, iterates tracer callbacks, inserts entries into an rb-tree, then serves seq_file reads. Release clears the snapshot. Unregister removes the file and session.

## State and Persistence Behavior

Global state is `all_stat_sessions` and `stat_dir`. Each session persists a tracer pointer, rb-tree snapshot, mutex, and dentry. Statistic entries are transient per open and released through `stat_release()` when supplied.

## Dependencies and Integration Points

It depends on `trace_stat.h`, tracefs, seq_file, rbtrees, security lockdown, and tracer-provided callbacks.

## Risks and Edge Cases

Partial insertion failure must release captured entries. Sorting treats `result >= 0` as left. `dummy_cmp()` mutates `ts->stat_cmp`. Duplicate detection is by pointer, so name collisions rely on tracefs creation failure.

## Test Signals

Register fake stat tracers, read headers and sorted rows, exercise no-entry output, allocation failure cleanup, unregister behavior, `stat_release` calls, and lockdown blocking.
