# sources/distributed-fs/ceph-client/kernel/bpf/stream.c

## Purpose
`stream.c` implements per-BPF-program stdout/stderr style streams used by BPF diagnostics and kfuncs. It provides lockless append paths for formatted messages, mutex-protected userspace reads, staging buffers for atomic multi-line commits, and stack-dump formatting that can annotate BPF instruction pointers with source file and line information.

## Important APIs, Types, and Functions
Internal stream element helpers are `bpf_stream_elem_init()`, `bpf_stream_elem_alloc()`, `__bpf_stream_push_str()`, `bpf_stream_consume_capacity()`, `bpf_stream_release_capacity()`, and `bpf_stream_push_str()`. Backlog/read helpers are `bpf_stream_backlog_peek()`, `bpf_stream_backlog_pop()`, `bpf_stream_backlog_fill()`, `bpf_stream_consume_elem()`, and `bpf_stream_read()`. Public program lifecycle/read functions are `bpf_prog_stream_init()`, `bpf_prog_stream_free()`, and `bpf_prog_stream_read()`.

The BPF kfuncs are `bpf_stream_vprintk()` and `bpf_stream_print_stack()`. Staging APIs used by in-kernel diagnostics include `bpf_stream_stage_init()`, `bpf_stream_stage_free()`, `bpf_stream_stage_printk()`, `bpf_stream_stage_commit()`, and `bpf_stream_stage_dump_stack()`. `dump_stack_cb()` is the architecture stack-walk callback that formats symbols and BPF file/line annotations.

## Control Flow
Producers validate stream ids with `bpf_stream_get()`, reserve capacity atomically, allocate a `bpf_stream_elem`, copy the string, and push it onto an `llist_head`. `bpf_stream_vprintk()` prepares binary printf arguments with `bpf_bprintf_prepare()`, formats into a BPF printf buffer, pushes the formatted bytes excluding the terminating NUL, and cleans up. Staged logging accumulates elements on a local `bpf_stream_stage`; commit reserves total capacity once, drains the stage list, finds its tail, and appends the batch to the program stream.

Readers call `bpf_prog_stream_read()`, which takes the stream mutex, moves the lockless log list into FIFO backlog order with `llist_reverse_order()`, and copies element data to userspace. Elements can be partially consumed; `consumed_len` is restored if `copy_to_user()` fails. Fully consumed elements release capacity and are freed.

Stack dump flow prints a CPU/UID/PID/comm header, prints `Call trace:`, walks the architecture BPF stack, resolves each IP through `bpf_prog_ksym_find()`, optionally maps it to BPF source file/line with `bpf_prog_get_file_line()`, and appends formatted frames to the stage before commit by the caller.

## State and Persistence Behavior
Each `struct bpf_prog_aux` owns two `struct bpf_stream` instances, indexed as `BPF_STDOUT` and `BPF_STDERR`. A stream tracks atomic queued capacity, a lockless producer log, a mutex-protected FIFO backlog, and backlog head/tail pointers. Elements persist until read or program stream free. Capacity is bounded by `BPF_STREAM_MAX_CAPACITY`; staged logs are temporary and must be freed or committed. No data persists after the BPF program is freed.

## Dependencies and Integration Points
The file depends on BPF program and aux structures, BPF memory allocation (`kmalloc_nolock`/`kfree_nolock`), linked-list primitives, mutexes, atomics, userspace copy helpers, BPF printf formatting buffers, credentials/current task state, architecture BPF stack walking, kallsyms-like BPF program lookup, and source-line lookup. It integrates with `rqspinlock.c` diagnostics through `bpf_stream_stage`, and with user-facing program stream read paths elsewhere in BPF filesystem or syscall plumbing.

## Risks and Test Signals
Important risks include capacity leaks on failed staged commits with a non-empty list, FIFO ordering mistakes when moving from lockless log to backlog, partial-read accounting bugs, `copy_to_user()` rollback errors, allocation in contexts where `kmalloc_nolock()` can fail, and stack dump recursion or symbol lookup races. Test signals include concurrent producers with userspace readers, stdout/stderr id validation, capacity-limit enforcement, partial reads over element boundaries, read fault rollback, program teardown with unread log/backlog data, `bpf_stream_vprintk()` argument validation, staged multi-line commit ordering, stack dump formatting, and integration tests that verify resilient-spinlock violations appear on stderr.
