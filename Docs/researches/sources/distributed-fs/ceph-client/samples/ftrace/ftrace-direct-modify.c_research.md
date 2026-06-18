# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-modify.c

Purpose: demonstrates replacing an ftrace direct trampoline at runtime for a single traced function (`schedule`).

Important APIs/functions: architecture-specific `my_tramp1`/`my_tramp2`, `my_direct_func1`, `my_direct_func2`, `struct ftrace_ops`, `ftrace_set_filter_ip`, `register_ftrace_direct`, `modify_ftrace_direct`, `unregister_ftrace_direct`, and a kernel thread.

Control flow: init filters the ops to `schedule`, registers `my_tramp1`, and starts a thread. Every two seconds the thread toggles between trampolines via `modify_ftrace_direct`; exit stops the thread and unregisters the current direct trampoline.

State and persistence: global direct ops, current trampoline address, trampoline array, and worker task. Runtime-only.

Dependencies and integration: depends on ftrace direct support and correct per-architecture calling convention assembly.

Risks: incorrect trampoline register preservation can crash the kernel. Tracing `schedule` is high frequency; `trace_printk` can perturb scheduling. Exit assumes `simple_tsk` was created when registration succeeded.

Test signals: load module and inspect trace buffer for alternating direct function messages; unload and verify direct registration is removed cleanly.
