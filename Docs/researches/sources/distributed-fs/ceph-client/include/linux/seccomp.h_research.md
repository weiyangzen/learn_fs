# sources/distributed-fs/ceph-client/include/linux/seccomp.h

Purpose: `seccomp.h` exposes kernel-side seccomp entry points, filter lifecycle hooks, user-facing prctl helpers, checkpoint/restore inspection hooks, and compile-time stubs when seccomp is disabled.

Important APIs/types/functions: It defines `SECCOMP_FILTER_FLAG_MASK`, notification addfd size constants, `secure_computing()`, `__secure_computing()`, `secure_computing_strict()`, `prctl_get_seccomp()`, `prctl_set_seccomp()`, `seccomp_mode()`, `seccomp_filter_release()`, `get_seccomp_filter()`, `seccomp_get_filter()`, `seccomp_get_metadata()`, and optional `proc_pid_seccomp_cache()`.

Control flow: On syscall entry, architectures with filter support call `secure_computing()`, which checks syscall work for `SECCOMP` and calls `__secure_computing()` only when needed. Prctl/syscall paths set or query mode and filter state. Task teardown releases filter references, and checkpoint/restore paths can read filters/metadata when configured.

State and persistence behavior: Per-task seccomp state lives in `struct seccomp` from `seccomp_types.h`, including mode, filter count, and active filter pointer. Filter references must be retained and released across task lifetime and clone paths. Disabled configs return `-EINVAL` or no-op values.

Dependencies and integration points: It depends on UAPI seccomp constants, thread-info syscall work flags, architecture seccomp support, BPF filter implementation, checkpoint/restore, procfs cache debug, and task lifecycle.

Risks: `secure_computing()` is syscall-hot; added work there impacts every syscall. Filter pointer access is lockless from current-task context and relies on lifecycle rules. Flag masks must track UAPI additions or userspace may pass unsupported flags incorrectly.

Test signals: Syscall filter allow/deny/trap/user notification, strict mode, TSYNC and TSYNC_ESRCH, disabled config stubs, checkpoint/restore filter export, task exit filter release, and proc seccomp cache debug when enabled.
