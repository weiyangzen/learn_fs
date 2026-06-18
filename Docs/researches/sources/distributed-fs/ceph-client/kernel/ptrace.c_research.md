# sources/distributed-fs/ceph-client/kernel/ptrace.c

## Purpose
`ptrace.c` provides the architecture-independent ptrace syscall core. It manages tracee attachment, permission checks, parent/child ptrace linkage, traced-task freezing, detach/reap behavior, tracee memory access, signal/regset/syscall-info requests, seccomp/rseq/syscall-user-dispatch requests, and compat syscall dispatch.

## Important APIs, types, and functions
Key exported or shared functions include `ptrace_access_vm()`, `__ptrace_link()`, `__ptrace_unlink()`, `ptrace_may_access()`, `exit_ptrace()`, `ptrace_readdata()`, `ptrace_writedata()`, `ptrace_request()`, `generic_ptrace_peekdata()`, `generic_ptrace_pokedata()`, and compat variants. Internal control helpers include `ptrace_check_attach()`, `ptrace_freeze_traced()`, `ptrace_unfreeze_traced()`, `__ptrace_may_access()`, `ptrace_attach()`, `ptrace_traceme()`, `ptrace_detach()`, `ptrace_resume()`, regset helpers, and syscall-info get/set helpers.

## Control flow
`SYSCALL_DEFINE4(ptrace)` handles `PTRACE_TRACEME` directly, looks up the target task, routes attach/seize through `ptrace_attach()`, otherwise verifies the task is traced by current and frozen unless the request allows asynchronous state. Architecture-specific `arch_ptrace()` gets first chance for requests; common `ptrace_request()` handles generic operations. Resume requests update syscall tracing flags, single-step/block-step state, exit signal, and wake the tracee. Detach disables arch-specific tracing, restores parentage, handles stopped state, and notifies proc connector.

## State and persistence behavior
Ptrace state lives in `task_struct`: `ptrace` flags, parent/real_parent, ptraced lists, `ptracer_cred`, jobctl flags, `last_siginfo`, `ptrace_message`, blocked masks, and syscall work bits. Attach persists until detach, tracer exit, tracee exit, or exec-specific transitions. Memory access is transient through `access_remote_vm()` after dumpability and credential checks.

## Dependencies and integration points
The file integrates tasklist locking, sighand locks, credentials, user namespaces, capabilities, LSM hooks, audit, proc connector, signals/job control, seccomp, rseq, syscall user dispatch, arch ptrace hooks, user regsets, compat siginfo/iovec handling, and remote memory GUP flags.

## Risks and invariants
Permission ordering is security critical: credentials are read before dumpability with an `smp_rmb()` pairing `commit_creds()`. Tasklist and sighand locks protect parentage and stop-state transitions. `JOBCTL_PTRACE_FROZEN` prevents tracees from running during sensitive operations. Detach and tracer-exit paths must correctly handle zombies and group stops. Compat and syscall-info setters must validate sizes, reserved fields, and sign extension to avoid ABI corruption.

## Test signals
Signals include ptrace selftests for attach/seize/traceme, permission denial across UIDs/user namespaces/dumpability, signal injection, group-stop/listen/interrupt semantics, regset get/set, syscall-info get/set, seccomp filter/metadata, rseq configuration, memory peek/poke partial failures, tracer exit with zombies, and compat ptrace on supported architectures.
