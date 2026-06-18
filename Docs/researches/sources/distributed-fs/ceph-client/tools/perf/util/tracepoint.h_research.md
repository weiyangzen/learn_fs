# sources/distributed-fs/ceph-client/tools/perf/util/tracepoint.h

## Purpose

`tracepoint.h` declares tracepoint validation helpers and directory iteration macros.

## Important APIs, Types, and Functions

It declares `tp_event_has_id()` and `is_valid_tracepoint()`. `for_each_event` iterates tracepoint event directories that are not `.`/`..` and have an `id` file. `for_each_subsystem` iterates tracepoint subsystem directories.

## Control Flow and State

The macros embed filtering logic around `readdir()` and call `tp_event_has_id()` for event validation.

## Dependencies and Integration Points

It depends on `dirent`, `string`, and bool support. It is used by trace metadata capture and tracepoint discovery.

## Risks and Test Signals

Macros can be surprising because they expand to `while` plus `if` blocks. Tests should exercise iteration with fake tracefs directories and ensure non-events are skipped.
