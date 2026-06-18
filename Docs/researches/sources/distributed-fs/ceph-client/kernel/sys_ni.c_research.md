# sources/distributed-fs/ceph-client/kernel/sys_ni.c

## Purpose
`sys_ni.c` provides weak/fallback entries for system calls that are not implemented by the current architecture or kernel configuration. Missing syscalls resolve to `sys_ni_syscall()` and return `-ENOSYS`.

## Important APIs, types, and functions
- `sys_ni_syscall()`: generic not-implemented syscall body.
- `COND_SYSCALL(name)` and `COND_SYSCALL_COMPAT(name)`: macros that map missing `sys_*` or `compat_sys_*` symbols to conditional syscall stubs, optionally overridden by architecture syscall wrapper support.
- The ordered list mirrors `include/uapi/asm-generic/unistd.h`, followed by architecture-specific, deprecated, obsolete, restartable sequence, uprobe, and uretprobe entries.

## Control flow
There is no runtime dispatch beyond a caller landing in a missing syscall stub and receiving `-ENOSYS`. Compile/link-time `cond_syscall()` machinery resolves absent implementations in the syscall table.

## State and persistence behavior
No state is read or written.

## Dependencies and integration points
It depends on architecture syscall wrapper conventions, `asm/unistd.h`, and weak syscall resolution. The file is part of the syscall table link contract, especially for optional features like AIO, io_uring, ipc, sockets, timers, BPF, seccomp, fanotify, memory policy, compat time32, and arch-specific syscalls.

## Risks
Ordering drift from `asm-generic/unistd.h` or missing a new optional syscall can create link failures or wrong ABI behavior. Accidentally providing a fallback for a syscall that should be mandatory can hide configuration bugs; omitting one can break allmodconfig/defconfig variants.

## Test signals
Build matrix coverage across architectures and feature configs is primary. Runtime tests should observe `ENOSYS` for configured-out optional syscalls and real behavior for enabled syscalls.
