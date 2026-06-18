# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-multi.c

Purpose: static multi-function ftrace direct-call sample.

Important APIs/functions: architecture-specific `my_tramp`, `my_direct_func(unsigned long ip)`, `struct ftrace_ops`, `ftrace_set_filter_ip`, `register_ftrace_direct`, and `unregister_ftrace_direct`.

Control flow: init filters both `wake_up_process` and `schedule`, registers `my_tramp`, and direct calls `my_direct_func` with the traced instruction pointer. Exit unregisters the direct call.

State and persistence: one `ftrace_ops` object and registered trampoline while loaded.

Dependencies and integration: depends on ftrace direct multi-target support and arch assembly.

Risks: probing scheduler paths with `trace_printk` is invasive. Any argument/IP recovery bug is architecture-specific and severe.

Test signals: load, generate scheduler/wakeup activity, read ftrace output for `ip` lines, and unload.
