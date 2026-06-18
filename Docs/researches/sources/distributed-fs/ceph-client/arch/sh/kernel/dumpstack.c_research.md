# sources/distributed-fs/ceph-client/arch/sh/kernel/dumpstack.c

Purpose: provides SH stack, memory, and symbol dump helpers used by oops, warnings, and diagnostics.

Important APIs and control flow: `dump_mem()` prints aligned 32-byte rows with fault-tolerant `__get_user()` reads. `printk_address()` formats reliable or questionable symbols. `stack_reader_dump()` scans a stack range for kernel text addresses and optionally expands function-graph tracer return addresses. `show_trace()` invokes `unwind_stack()` with print callbacks, and `show_stack()` prints task identity, raw stack memory, and trace.

State, dependencies, and risks: state is transient scan position plus function graph ret-stack index. Dependencies include the active unwinder, kallsyms, task stack helpers, ftrace graph tracing, and kernel text address validation. Stack scanning can produce false positives and unreliable callchains when unwind metadata is absent. Test signals are panic/oops readability, function-graph tracing interaction, and stacktrace self-tests if enabled.
