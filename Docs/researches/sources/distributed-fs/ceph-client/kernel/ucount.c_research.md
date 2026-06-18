<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ucount.c -->
# sources/distributed-fs/ceph-client/kernel/ucount.c

Purpose: manages per-user, per-user-namespace usage counters and rlimit accounting across namespace ancestry. It backs limits such as max user namespaces, PID namespaces, UTS namespaces, inotify/fanotify counts, and rlimit-style counts.

Important APIs and state: `init_ucounts` is the root counter object. `alloc_ucounts()`, `put_ucounts()`, `inc_ucount()`, and `dec_ucount()` manage namespace object counters. Rlimit helpers include `inc_rlimit_ucounts()`, `dec_rlimit_ucounts()`, `inc_rlimit_get_ucounts()`, `dec_rlimit_put_ucounts()`, and `is_rlimit_overlimit()`. `setup_userns_sysctls()` and `retire_userns_sysctls()` expose per-namespace `/proc/sys/user/*` knobs.

Control flow: ucounts are hashed by namespace pointer plus kuid and protected by RCU plus `ucounts_lock` for insertion/removal. Allocation double-checks under lock to avoid duplicate objects. `inc_ucount()` allocates the leaf object, then walks parent `ns->ucounts` chain, incrementing each atomic count only below that namespace's max; on failure it unwinds prior increments and drops the leaf reference. Rlimit functions similarly walk ancestors and maintain references when counts transition from zero.

State and persistence: counters are in-memory, reference-counted by `rcuref`, and freed with RCU. Sysctl tables are dynamically duplicated per user namespace and point into `ns->ucount_max`.

Dependencies and integration: integrates with user namespace creation, UTS namespaces, pid/ipc/net/mount/cgroup/time namespaces, inotify/fanotify, and proc sysctl. Permissions allow CAP_SYS_RESOURCE in the target namespace to write limits.

Risks: ancestor unwind correctness is critical to avoid leaked counts. Negative atomic results are WARNed. Sysctl table lifetime must match namespace lifetime. Test signals include namespace creation at limits, concurrent alloc/free for same uid, sysctl permission checks in nested namespaces, and rlimit ref transitions to and from zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ucount.c -->
