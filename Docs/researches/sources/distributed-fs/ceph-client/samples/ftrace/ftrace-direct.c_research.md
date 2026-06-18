# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct.c

Purpose: minimal ftrace direct-call sample for `wake_up_process`.

Important APIs/functions: `my_direct_func(struct task_struct *p)`, architecture-specific `my_tramp`, `ftrace_set_filter_ip`, `register_ftrace_direct`, and `unregister_ftrace_direct`.

Control flow: init filters `wake_up_process` and registers the trampoline; the direct function logs the woken task’s command and pid. Exit unregisters the trampoline.

State and persistence: single global `ftrace_ops` while loaded.

Dependencies and integration: ftrace direct and architecture trampoline support.

Risks: wakeup paths are frequent; logging can cause overhead. Architecture assembly must preserve calling context.

Test signals: load, trigger task wakeups, inspect trace buffer for task names, unload.
