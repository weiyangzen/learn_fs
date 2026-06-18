# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/mount.h

## Purpose
Provides nolibc compatibility for mount operations.

## APIs, Types, and Functions
Defines `_sys_mount`, `mount`, `_sys_umount2`, and `umount2` and includes the relevant Linux UAPI constants when needed.

## Control Flow, State, and Persistence
The wrapper forwards filesystem type, source, target, flags, data, and unmount flags to kernel mount syscalls, then translates kernel errors with `__sysret` where appropriate. It retains no userspace state; effects are entirely in kernel process, filesystem, tracing, entropy, or system-control state.

## Dependencies and Integration
Depends on `../arch.h`, `../sys.h`, `../types.h` where required, and Linux UAPI headers for constants and structures. It integrates with nolibc programs that expect the corresponding `<sys/...h>` include path.

## Risks and Test Signals
Risks are permission-sensitive failure paths, kernel-version syscall availability, pointer argument lifetime, and differences from full libc wrappers. Test signals include invalid argument tests, expected `EPERM`/`EINVAL` paths, successful smoke tests where safe, and cross-architecture compilation.
