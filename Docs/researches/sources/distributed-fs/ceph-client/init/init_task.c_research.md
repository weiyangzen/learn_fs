# sources/distributed-fs/ceph-client/init/init_task.c

## Purpose
`init_task.c` defines the statically allocated initial task, signal/sighand/credential/group state, optional shadow call stack, and initial thread_info for the primordial kernel task.

## Important APIs, Types, and Functions
Important objects are `init_signals`, `init_sighand`, optional `init_shadow_call_stack`, `init_groups`, `init_cred`, exported `init_task`, and optional `init_thread_info`. The initializer covers scheduler entities, CPU masks, mm/files/fs/nsproxy, credentials, signal state, timers, audit/perf/RCU/cpuset/RT mutex/NUMA/KASAN/KCSAN/lockdep/tracing/livepatch/security/seccomp/SCHED_MM_CID fields depending on config.

## Control Flow
There are no runtime functions. The compiler and linker place fully initialized objects into the kernel image. Early boot starts from this task context; later fork/exec/scheduler code treats it as PID 0/kthreadd lineage root and a never-freed anchor for shared initial structures.

## State and Persistence Behavior
This file defines persistent kernel-lifetime state. Reference counts are initialized so the initial task, credentials, and groups are not freed. The task starts as `PF_KTHREAD`, uses `init_mm`, root credentials with full capabilities, default signal dispositions, and root namespace/filesystem structures.

## Dependencies and Integration Points
It depends on many subsystem initializer macros and config blocks: scheduler, credentials, namespace, files, signals, POSIX timers, cgroups, RCU, perf, audit, tracing, security, seccomp, and architecture thread initialization. `EXPORT_SYMBOL(init_task)` makes the object available to modules/core code.

## Risks and Test Signals
Risks include missing initializer fields after `task_struct` changes, config-conditional layout drift, incorrect reference counts, wrong root credentials/capabilities, lockdep/tracing initial state mistakes, and linker alignment requirements for `thread_info`. Test signals include compile-time designated-initializer coverage across config matrices, early boot smoke tests, lockdep/RCU/perf/audit enabled boots, and static checks for new `task_struct` fields.
