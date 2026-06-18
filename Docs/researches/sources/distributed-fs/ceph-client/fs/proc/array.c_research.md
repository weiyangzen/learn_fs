# sources/distributed-fs/ceph-client/fs/proc/array.c

Purpose: Formats per-task proc status/stat/statm data and the optional `/proc/<pid>/task/<tid>/children` file.

Important APIs and types: Public entry points include `proc_task_name()`, `render_sigset_t()`, `proc_pid_status()`, `proc_tid_stat()`, `proc_tgid_stat()`, `proc_pid_statm()`, and, under `CONFIG_PROC_CHILDREN`, `proc_tid_children_operations`. It works with `task_struct`, `signal_struct`, `mm_struct`, `pid_namespace`, `cred`, signal sets, capabilities, cpumasks, time namespaces, delay accounting, and architecture hooks such as `arch_proc_pid_thread_features()`.

Control flow: Status output starts with task name, then emits state, IDs, credentials, namespace PID views, memory data, signal sets, capabilities, seccomp/speculation state, CPU affinity, cpuset data, context-switch counts, and optional architecture fields. `do_task_stat()` collects task/session/tty/fault/cputime/mm data under the appropriate locks, applies ptrace restrictions to sensitive addresses, converts boot time through time namespaces, and emits the legacy space-delimited `/proc/<pid>/stat` layout. `proc_pid_statm()` emits virtual memory counters from `task_statm()`. The children seq file walks the parent task's children under `tasklist_lock`, with a fast continuation path when the previous pid is still valid.

State and persistence: It does not store proc state; it snapshots live task, signal, mm, credential, and namespace state when files are read. Values can race with task exit or mutation by design, and references such as `get_task_mm()` and `get_task_cred()` bound object lifetime during formatting.

Dependencies and integration points: Called by the pid entry tables in `base.c`. Integrates with scheduler accounting, ptrace permission checks, memory management, cpusets, capabilities, seccomp, time namespaces, NUMA balancing, coredump state, and procfs seq/file operations.

Risks: `/proc/<pid>/stat` is ABI-sensitive and field order must remain stable. Address and wchan exposure must obey ptrace gating to avoid information leaks. Children enumeration is explicitly approximate under concurrent exit and can skip tasks. The code must avoid holding locks while doing slow seq output except for short protected snapshots.

Test signals: Compare `/proc/self/status`, `stat`, and `statm` field formats with procps expectations; test non-dumpable and ptrace-denied processes; PID namespaces; time namespaces; kthreads/workqueue names; seccomp/capability output; coredump state; and `CONFIG_PROC_CHILDREN` with concurrent child exits.
