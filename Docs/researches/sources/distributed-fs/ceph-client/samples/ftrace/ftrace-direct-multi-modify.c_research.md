# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-multi-modify.c

Purpose: demonstrates runtime trampoline replacement for one ftrace direct registration attached to multiple functions.

Important APIs/functions: `ftrace_set_filter_ip` for `wake_up_process` and `schedule`, `register_ftrace_direct`, `modify_ftrace_direct`, `unregister_ftrace_direct`, architecture trampolines that pass the traced IP to `my_direct_func1/2`.

Control flow: init filters both functions and registers one direct trampoline. A kernel thread toggles the direct target every two seconds. Exit stops the thread and unregisters the current trampoline.

State and persistence: global trampoline pointer, two trampoline addresses, ftrace ops, and task pointer.

Dependencies and integration: integrates with multi-function ftrace direct support and architecture-specific ftrace ABI.

Risks: same trampoline must safely handle both traced functions and preserve arguments. Logging from scheduler/wakeup paths can be noisy and timing-sensitive.

Test signals: load with `CONFIG_SAMPLE_FTRACE_DIRECT_MULTI`, trigger scheduling/wakeup activity, confirm trace messages include IP values and alternate functions, then unload.
