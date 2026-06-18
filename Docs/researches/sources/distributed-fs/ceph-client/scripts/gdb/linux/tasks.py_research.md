# sources/distributed-fs/ceph-client/scripts/gdb/linux/tasks.py

## Purpose
`tasks.py` exposes Linux task iteration, PID lookup, process listing, and `thread_info` lookup for GDB scripts.

## Important APIs, Types, and Functions
`task_lists()` walks `init_task` and each signal thread list. `get_task_by_pid()` returns the first matching task. `$lx_task_by_pid`, `lx-ps`, `$lx_thread_info`, and `$lx_thread_info_by_pid` are registered GDB interfaces. `get_thread_info()` handles both embedded and stack-based `thread_info`.

## Control Flow
Task traversal iterates every thread in each thread group through `signal.thread_head`, then advances the global process list through `task.tasks.next`. Commands format task address, PID, and `comm`, or return thread info.

## State and Persistence Behavior
Read-only. Results reflect the stopped target's current task lists with no locking or snapshot.

## Dependencies and Integration Points
It depends on `lists.py` and `utils.container_of()`. `proc.py` uses `get_task_by_pid()` for mount namespace lookup.

## Risks and Test Signals
Corrupt task lists can loop or dereference invalid pointers. PID namespaces are not modeled; lookup compares raw `task_struct.pid`. Test with multi-threaded processes, kernel threads, PID 1, and architectures with embedded versus stack `thread_info`.
