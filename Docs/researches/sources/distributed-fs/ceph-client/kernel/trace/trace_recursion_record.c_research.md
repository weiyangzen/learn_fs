# sources/distributed-fs/ceph-client/kernel/trace/trace_recursion_record.c

## Purpose

`trace_recursion_record.c` records ftrace callbacks that triggered recursion and exposes them through tracefs as `recursed_functions`. The complete 233-line file was read.

## Important APIs, Types, and Functions

The exported API is `ftrace_record_recursion()`. Internal state includes `struct recursed_functions`, a fixed `recursed_functions[]` array, `nr_records`, and `cached_function`. Tracefs support is implemented with seq operations and `recursed_function_open()`.

## Control Flow

Recording checks the cached IP, reads `nr_records`, searches existing entries, and uses `cmpxchg()` to reserve a slot. If another writer wins, it advances to another slot instead of spinning. Opening with write and truncate clears records by setting `nr_records` to `-1`, zeroing the array, and restoring zero. Reads format parent and child symbols through `trace_seq`.

## State and Persistence Behavior

Records persist globally until the tracefs file is truncated. `nr_records == -1` blocks writers during clear. `cached_function` is deliberately racy. Read formatting uses a global `trace_seq` pointer under `recursed_function_lock`.

## Dependencies and Integration Points

It integrates with ftrace recursion protection, tracefs, seq_file, kallsyms symbol formatting, and trace output helpers.

## Risks and Edge Cases

Recording is best-effort. Concurrent writers may skip duplicates or use later slots. A full array silently stops recording. Clearing can race with writers; the accepted worst case is a zero entry that can be recorded again later.

## Test Signals

Use ftrace recursion selftests, tracefs reads, truncation clears, concurrent recursion from multiple CPUs, array-full behavior, and symbol formatting checks.
