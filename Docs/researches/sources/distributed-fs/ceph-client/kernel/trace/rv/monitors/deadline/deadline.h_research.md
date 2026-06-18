# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/deadline.h

## Purpose

This shared header provides helper logic for the deadline runtime-verification monitor family. It normalizes deadline task/server identity, syscall policy extraction, task and server storage initialization, and task lifecycle callbacks used by deadline child monitors such as `nomiss`.

## Important APIs, Types, and Functions

The header exports `rv_deadline` and `rv_ext_sched_class`, defines `should_skip_syscall_handle()`, `is_supported_type()`, `is_server_type()`, `fair_server_id()`, `ext_server_id()`, `get_entity_id()`, `task_is_scx_enabled()`, `EXPAND_ID`, `EXPAND_ID_TASK`, `get_server_type()`, and `extract_params()`. When included with `RV_MON_TYPE`, it also provides `get_server()`, `init_storage()`, `handle_newtask()`, and `handle_exit()` for DA/HA monitor storage.

## Control Flow

Deadline monitor C files include this header after setting monitor macros, then use the ID helpers from tracepoint handlers. `extract_params()` decodes `sched_setscheduler` and `sched_setattr` syscall arguments, rejects `SCHED_FLAG_KEEP_POLICY`, and returns the new policy stripped of `SCHED_RESET_ON_FORK`. `init_storage()` pre-allocates fair and sched-ext server slots per possible CPU, optionally walks the task list to create storage for existing `SCHED_DEADLINE` tasks, and destroys the monitor on allocation failure.

## State and Persistence Behavior

The header itself persists no state, but it defines the ID scheme that makes monitor state stable across events: positive task PIDs for tasks, negative CPU-derived IDs for fair and sched-ext deadline servers, and `NO_SERVER_ID` for unknown server types. Storage is in monitor-owned DA/HA objects and is rebuilt on monitor enable/reset.

## Dependencies and Integration Points

It depends on deadline scheduler internals, syscall argument helpers, `sched_attr`, tasklist traversal, sched-class extension support, and RV DA/HA helper APIs. It integrates child monitors with `sched_dl_*`, `sched_switch`, `task_newtask`, `sched_process_exit`, and syscall tracepoints.

## Risks and Edge Cases

Negative server IDs assume the number of possible CPUs bounds the server namespace. The syscall parser deliberately copies only up to `sched_flags`, so changes in syscall ABI semantics must be reflected here. `get_server()` may rely on pre-created storage because allocating from deadline server tracepoints can deadlock. Task exit destroys only deadline-task storage, so policy transitions are handled by child monitors.

## Test Signals

Useful checks include enabling deadline monitors on systems with and without syscall tracepoints, changing policies via `sched_setscheduler` and `sched_setattr`, deadline task fork/exit coverage, sched-ext enabled and disabled builds, and stress with fair-server tracepoints to verify negative IDs remain unique.
