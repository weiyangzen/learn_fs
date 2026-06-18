# sources/distributed-fs/openafs/src/afs/LINUX/osi_ioctl.c

## Purpose
This file creates the Linux procfs ioctl endpoint used to pass OpenAFS syscall requests from userspace into kernel `afs_syscall`.

## Important APIs, types, and functions
- `afs_ioctl` validates ioctl command numbers, copies `struct afsprocdata` or compat `struct afsprocdata32` from userspace, and calls `afs_syscall`.
- `afs_unlocked_ioctl` adapts the modern file ioctl signature.
- `afs_syscall_ops` is either `struct proc_ops` or `struct file_operations` depending on kernel support.
- `osi_ioctl_init` creates the proc entry named `PROC_SYSCALL_NAME`.
- `osi_ioctl_clean` removes that proc entry.

## Control flow and behavior
The ioctl path accepts only `VIOC_SYSCALL` and `VIOC_SYSCALL32`. On 32-bit compatibility syscalls when `NEED_IOCTL32` is enabled, it copies the 32-bit argument structure and widens fields before dispatching. Otherwise it copies the native structure. Copy failures return `-EFAULT`, bad commands return `-EINVAL`, and `afs_syscall` returns the actual AFS operation result.

## State and persistence
The file creates/removes a procfs node under `openafs_procfs`. It does not persist data beyond the proc entry lifecycle.

## Dependencies and integration points
It depends on `openafs_procfs` from `osi_proc.c` or PAG module init, compatibility wrappers in `osi_compat.h`, Linux procfs ioctl operations, `copy_from_user`, and the common `afs_syscall` dispatcher.

## Risks
The proc entry is created with mode `0666`, so validation must rely on `afs_syscall` and downstream authorization. Compat argument translation must match userspace structure layout exactly. The init code does not report failure if proc creation returns NULL, so later user tools may fail with missing endpoint.

## Test signals
Test native and compat ioctl dispatch, invalid command rejection, bad user pointer `-EFAULT`, proc entry create/remove on module load/unload, and permission/authorization behavior for privileged and unprivileged callers.
