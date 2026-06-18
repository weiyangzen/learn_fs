# sources/distributed-fs/ceph-client/kernel/trace/trace_pid.c

## Purpose
Implements helper logic for tracing PID filters: membership checks, ignore decisions, fork/exit propagation, seq_file iteration, and user writes that construct new PID filter lists atomically.

## APIs, Control Flow, and State
`trace_find_filtered_pid()` wraps `trace_pid_list_is_set()`. `trace_ignore_this_task()` applies include and exclude lists: a task is ignored if an include list exists and lacks the PID, or if an exclude list contains the PID. `trace_filter_add_remove_task()` propagates PID filters across forks when the parent is included and removes PIDs on exit when `self` is NULL.

Seq-file helpers are `trace_pid_start()`, `trace_pid_next()`, and `trace_pid_show()`. They iterate `trace_pid_list` bitsets while returning `pid + 1` as the cursor so PID 0 can be represented without colliding with NULL. `trace_pid_write()` parses user input with a `trace_parser`, builds a completely new `trace_pid_list`, copies existing filtered PIDs first, parses numeric PIDs from the write buffer, and only publishes the new list through `*new_pid_list` if the whole write succeeds. An empty successful write clears the list by returning NULL.

## Dependencies, Integration, Risks, and Tests
The file depends on `trace_pid_list` helpers, `trace_parser`, user-copy helpers in tracing code, task PIDs, and seq_file. It integrates with tracefs PID filter files such as tracing PID include/exclude controls and fork/exit tracing propagation.

Risks include partial-write semantics, PID truncation from unsigned long to `pid_t`, memory allocation failures, all-or-nothing list replacement expectations, and cursor arithmetic around PID 0. Tests should cover adding multiple PIDs, clearing lists, malformed input rollback, copying an existing list while adding more PIDs, include/exclude precedence, fork propagation only from listed parents, exit removal, and seq iteration including PID 0.
