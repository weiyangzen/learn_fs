<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_task.h -->
# sources/distributed-fs/ceph-client/include/linux/init_task.h

Purpose: Provides declarations and small initialization macros used while defining the kernel's initial task.

Important APIs/types/functions: Declares `init_files`, `init_fs`, and `init_nsproxy`; defines `INIT_PREV_CPUTIME(x)` for non-native virtual CPU accounting builds; defines `INIT_TASK_COMM` as `"swapper"`; and marks the initial thread-info storage with `__init_thread_info`.

Control flow: No runtime functions. The macros expand into the compile-time initializer for `init_task` and related structures.

State/persistence: The referenced files/fs/nsproxy objects and swapper task identity are permanent baseline kernel state.

Dependencies/integration: Includes RCU, IRQ flags, UTS, lockdep, ftrace, IPC, PID/user/net namespaces, securebits, seqlock, rbtree, refcount, scheduler, livepatch, mm types, and architecture thread info.

Risks: The initial task identity and thread-info placement are early-boot critical; accounting macro changes must match scheduler fields.

Test signals: Successful boot, virtual CPU accounting config builds, `comm` showing swapper for PID 0, and architecture thread-info alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_task.h -->
