<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stacktrace.h -->
# sources/distributed-fs/ceph-client/include/linux/stacktrace.h

Purpose: Declares generic and architecture stack-walking interfaces for saving, printing, and reliably collecting kernel/user stack traces.

Important APIs/types/functions: `stack_trace_consume_fn`, `arch_stack_walk()`, `arch_stack_walk_reliable()`, `arch_stack_walk_user()`, `stack_trace_print()`, `stack_trace_snprint()`, `stack_trace_save*()`, `filter_irq_stacks()`, legacy `struct stack_trace`, `save_stack_trace*()`, and `stack_trace_save_tsk_reliable()`.

Control flow: Architecture stack walkers call a consumer callback for each address. Generic save functions fill caller-provided arrays with optional skip counts. Reliable variants return errors for unsupported/unreliable stacks and require inactive pinned tasks when walking non-current tasks.

State and persistence behavior: Stack traces are transient arrays of instruction pointers. The legacy `struct stack_trace` stores buffer, count, capacity, and skip state during collection.

Dependencies: Architecture unwind support, task and register structures, errno values, and `CONFIG_STACKTRACE`/`CONFIG_ARCH_STACKWALK`.

Integration points: Debugging, livepatch reliability checks, stack depot, tracing, warnings, and user stack capture.

Risks: Reliable walking has strict task-state requirements. Buffer size limits truncate traces. User stack walking depends on register validity and architecture support.

Test signals: Architecture unwind tests, reliable-stacktrace selftests, stack trace print/snprint tests, IRQ stack filtering tests, and disabled-config stub tests returning `-ENOSYS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stacktrace.h -->
