# sources/distributed-fs/ceph-client/kernel/sys.c

## Purpose
`sys.c` is a large collection of core process, credential, resource-limit, UTS, accounting, `prctl`, CPU, and system-information syscalls. It provides user/kernel ABI glue for identity changes, process groups/sessions, uname/hostname/domainname, rlimits, rusage, process controls, `getcpu()`, and `sysinfo()`.

## Important APIs, types, and functions
- Overflow identity sysctls: `overflowuid`, `overflowgid`, `fs_overflowuid`, `fs_overflowgid`, and `init_overflow_sysctl()`.
- Priority syscalls: `setpriority()`/`getpriority()` plus permission helpers `set_one_prio_perm()` and `set_one_prio()`.
- Credential syscalls under `CONFIG_MULTIUSER`: `__sys_setregid()`, `__sys_setgid()`, `__sys_setreuid()`, `__sys_setuid()`, `__sys_setresuid()`, `__sys_setresgid()`, `__sys_setfsuid()`, `__sys_setfsgid()`, and matching syscall wrappers/getters.
- Basic IDs/timing: `getpid()`, `gettid()`, `getppid()`, UID/GID getters, `times()`, compat `times()`.
- Process groups/sessions: `setpgid()`, `getpgid()`, `getsid()`, `ksys_setsid()`, `setsid()`.
- UTS operations: `newuname()`, legacy uname variants, `sethostname()`, `gethostname()`, `setdomainname()`.
- Resource usage/limits: `do_prlimit()`, `getrlimit()`, `setrlimit()`, `prlimit64()`, `getrusage()`, compat variants, `umask()`.
- `prctl()` and helpers for MM metadata, auxv, child subreaper, no-new-privs, THP disable, MDWE, syscall user dispatch, KSM, RISC-V/vector hooks, CFI/shadow stack hooks, timers, futex, rseq, and architecture-specific controls.
- Misc: `getcpu()`, `do_sysinfo()`, `sysinfo()`, compat `sysinfo()`.

## Control flow
Most syscalls validate user arguments, translate namespace IDs, perform capability/LSM checks, then update task, signal, mm, fs, or UTS state under the appropriate lock. Credential setters allocate new credentials with `prepare_creds()`, modify UID/GID fields, update user accounting/ucounts where needed, call LSM fixup hooks, flag deferred NPROC overflow, and `commit_creds()`. Process group/session syscalls hold `tasklist_lock` to stabilize parent and PID relationships. `prlimit64()` copies optional new limits, checks cross-task permissions under RCU, pins the target task, optionally holds `tasklist_lock`, calls `do_prlimit()`, and copies old limits back. `prctl()` first lets LSM handle options, then dispatches a large option switch to core or architecture hooks.

## State and persistence behavior
The file mutates long-lived kernel state: current credentials, user structs, ucounts, task nice values, signal rlimits/accounting, process group/session PID links, UTS namespace names, mm metadata and flags, task flags, timer slack, no-new-privs, KSM merge state, and filesystem umask. These changes persist for the task, thread group, namespace, or system until explicitly changed or the object exits. Sysinfo/getrusage/times are read-only snapshots.

## Dependencies and integration points
`sys.c` integrates with namespaces, credentials, capabilities, LSM hooks, proc connectors, scheduler/autogroup, PID/tasklist locking, UTS namespace notifications, resource limits, POSIX timers, memory management, checkpoint/restore, seccomp, perf, syscall user dispatch, futex, rseq, KSM, architecture prctl macros, time namespaces, memory statistics, and compat ABI conversion.

## Risks
This is security- and ABI-critical code. Risks include privilege escalation through incomplete namespace/capability checks, credential lifetime mistakes, tasklist/RCU races, ABI regressions in legacy/compat syscalls, integer conversion errors in rlimits/sysinfo, and unsafe `prctl(PR_SET_MM*)` validation. Many setters intentionally return old values or defer errors for historical compatibility, so behavior changes can break userspace.

## Test signals
Strong signals come from LTP syscall tests, kselftests for prctl/seccomp/rseq/futex/user namespaces, compat ABI testing, container namespace tests, rlimit/CPU timer tests, and security regression tests. Kernel warnings, LSM denials, failed copy_to/from_user paths, and tracepoint `task_prctl_unknown` are useful runtime indicators.
