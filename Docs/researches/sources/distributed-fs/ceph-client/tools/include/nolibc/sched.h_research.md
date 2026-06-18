# sources/distributed-fs/ceph-client/tools/include/nolibc/sched.h

## Purpose
Provides namespace and scheduling-adjacent wrappers for nolibc.

## APIs, Types, and Functions
Defines `_sys_setns`, `setns`, `_sys_unshare`, and `unshare`, and includes `<linux/sched.h>` for flag constants.

## Control Flow, State, and Persistence
Each wrapper passes fd or flag arguments to the corresponding syscall and returns through `__sysret`. No userspace state is persisted; effects are kernel task namespace or sharing-state changes.

## Dependencies and Integration
Depends on syscall numbers, `arch.h`, `sys.h`, and Linux scheduler UAPI. It integrates with container, namespace, and isolation tests that use nolibc.

## Risks and Test Signals
Risks are irreversible process-context changes in tests, flag availability across kernels, and permission-sensitive failures. Test signals are invalid flag/fd handling, user namespace or mount namespace smoke tests, and expected `EPERM` paths under unprivileged execution.
