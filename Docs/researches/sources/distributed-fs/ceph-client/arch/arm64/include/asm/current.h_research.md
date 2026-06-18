## sources/distributed-fs/ceph-client/arch/arm64/include/asm/current.h

Purpose: provides efficient access to the current task pointer on arm64.

Important APIs/types/functions: defines `get_current()` by reading `sp_el0`, then maps `current` to `get_current()`.

Control flow: single system-register read.

State and persistence: relies on context-switch and exception-entry code maintaining `sp_el0` as the current task pointer while in kernel mode.

Dependencies and integration: depends on sysreg helpers and task/thread setup. Used everywhere through `current`.

Risks: any mismatch between `sp_el0` maintenance and this helper corrupts current-task access globally. Test signals are context-switch stress, syscall/interrupt entry tests, CPU hotplug, and lockdep/scheduler sanity.
