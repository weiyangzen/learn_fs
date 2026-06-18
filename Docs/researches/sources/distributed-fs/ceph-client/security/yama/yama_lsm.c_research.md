# sources/distributed-fs/ceph-client/security/yama/yama_lsm.c

## Purpose

This file implements the Yama LSM's ptrace hardening policy. It restricts `PTRACE_ATTACH`, `PTRACE_TRACEME`, and related ptrace-like access according to `/proc/sys/kernel/yama/ptrace_scope`, while allowing explicit tracee-selected exceptions through `PR_SET_PTRACER`.

## Important APIs, types, and functions

The main state is `ptrace_scope`, `ptracer_relations`, and `ptracer_relations_lock`. `struct ptrace_relation` records one tracee's allowed tracer ancestor and an invalidation flag. Key functions are `yama_task_prctl`, `yama_ptracer_add`, `yama_ptracer_del`, `yama_relation_cleanup`, `task_is_descendant`, `ptracer_exception_found`, `yama_ptrace_access_check`, `yama_ptrace_traceme`, `yama_dointvec_minmax`, `yama_init_sysctl`, and `yama_init`. LSM hooks are ptrace access, ptrace traceme, task prctl, and task free.

## Control Flow

`PR_SET_PTRACER` records, replaces, clears, or broadens a tracee exception at process-group granularity. Ptrace attach checks consult `ptrace_scope`: disabled allows normal DAC, relational requires target to be a descendant, an explicit exception, or CAP_SYS_PTRACE in the target user namespace, capability mode requires CAP_SYS_PTRACE, and no-attach denies all attaches. `PTRACE_TRACEME` is denied in capability/no-attach modes unless the parent has the needed capability. Denials are reported through deferred task work when command-line access can sleep.

## State and Persistence

Ptracer exceptions live in an RCU-protected list. Task exit marks related relations invalid and schedules work to remove and free them with `kfree_rcu`. `ptrace_scope` persists as a sysctl value during runtime; once set to maximum scope, the sysctl handler locks the minimum to the maximum so it cannot be reduced.

## Dependencies and Integration Points

It depends on LSM hooks, sysctl, ptrace, prctl constants, RCU, spinlocks, task work, task lifetime helpers, user namespace capability checks, and ratelimited logging. It registers with `DEFINE_LSM(yama)`.

## Risks and Test Signals

Risks include stale task pointers in exception records, lock ordering around task locks and RCU, namespace capability semantics, one-exception-per-tracee replacement behavior, and irreversible max-scope sysctl behavior. Tests should cover all `ptrace_scope` values, `PR_SET_PTRACER` pid/ANY/clear flows, task exit cleanup, namespace capability cases, `PTRACE_MODE_NOAUDIT`, and concurrent prctl/exit/attach races.
