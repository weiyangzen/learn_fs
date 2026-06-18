<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_syscalls.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_syscalls.c

Purpose: implements ftrace/perf trace events for syscall entry and exit. It maps syscall numbers to `struct syscall_metadata`, creates trace event classes for `sys_enter_*` and `sys_exit_*`, formats event output, and optionally snapshots selected user-space arguments into dynamic trace fields for more useful syscall records.

Important APIs and data: `init_ftrace_syscalls()` builds `syscalls_metadata` or the sparse xarray from linker-provided syscall metadata and `arch_syscall_addr()`. `get_syscall_name()` exposes metadata lookup. `event_class_syscall_enter` and `event_class_syscall_exit` provide raw initialization, field definitions, and registration callbacks. `check_faultable_syscall()` annotates metadata with `user_mask`, `user_arg_size`, and `user_arg_is_str` for syscalls whose pointer arguments are copied.

Control flow: enable paths call `syscall_enter_register()` or `syscall_exit_register()`, then `reg_event_syscall_enter()`/`reg_event_syscall_exit()` install global syscall tracepoint callbacks when the first event is enabled. `ftrace_syscall_enter()` validates the syscall number, finds the per-array `trace_event_file`, copies register arguments, optionally reads user memory through `trace_user_fault_read()`, reserves a ring buffer event, writes static args and dynamic data locations, and commits. Exit tracing writes syscall number plus return value. Perf mirrors the same entry/exit flow using `perf_trace_buf_alloc()` and BPF prefilters.

State and persistence: per-trace-array refcounts and file arrays decide which syscalls are active. `syscall_buffer` is a shared fault buffer with tracing refcounts and RCU Tasks Trace cleanup. Perf state uses bitmaps and global refcounts. There is no durable storage; events are transient ring-buffer or perf records.

Dependencies and integration: depends on arch syscall helpers, tracepoints `sys_enter`/`sys_exit`, trace event metadata, ring buffers, perf, BPF, xarray, and user access fault helpers. It integrates with tracefs event enablement and perf event registration.

Risks: incorrect syscall metadata mapping disables or mislabels events; compat syscall handling is arch-sensitive. Dynamic user copies must avoid faults and truncation bugs. Registration/unregistration races are protected by `syscall_trace_lock`, but lifetime depends on file pointers being published with `WRITE_ONCE()` and callback unregistration. Test signals include enabling individual syscall events, verbose openat formatting, perf+BPF syscall events, compat tasks, and syscalls with truncated/faulting user pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_syscalls.c -->
