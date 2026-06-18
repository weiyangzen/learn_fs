# sources/distributed-fs/ceph-client/tools/include/nolibc/sys.h

## Purpose
Provides the main nolibc syscall wrapper layer for process, filesystem, fd, identity, and basic memory-management operations.

## APIs, Types, and Functions
Defines `__sysret()` for libc-style error translation and `__nolibc_enosys()` for unavailable calls. Wrappers include `brk`, `sbrk`, `chdir`, `fchdir`, `chmod`, `chown`, `chroot`, `close`, `dup`, `dup2`, `dup3`, `execve`, `_exit`, `exit`, `fork`, `vfork`, `fsync`, `getdents64`, `geteuid`, `getpgid`, `getpgrp`, `getpid`, `getppid`, `gettid`, `getpagesize`, `getuid`, `kill`, `link`, `lseek`, `mkdir`, `rmdir`, `mknod`, `pipe2`, `pipe`, `pivot_root`, `read`, `sched_yield`, `setpgid`, `setpgrp`, `setsid`, `symlink`, `umask`, `umount2`, `unlink`, `write`, and `memfd_create`.

## Control Flow, State, and Persistence
Each `_sys_*` helper issues the raw syscall or architecture override; public wrappers pass results through `__sysret` when errno translation is needed. Many wrappers choose modern `*at` syscalls when legacy syscalls are missing, and `sbrk` persists the current break in static state after probing with `brk(NULL)`. Process-exit wrappers never return.

## Dependencies and Integration
Depends on `arch.h` syscall macros, errno handling, `types.h`, Linux syscall numbers, and architecture-specific overrides for special ABIs. It is the central dependency for stdio, stdlib, dirent, unistd, fcntl, and `sys/*` compatibility headers.

## Risks and Test Signals
Risks include syscall availability differences, subtle fallback semantics for `dup2`, `link`, `mkdir`, `mknod`, `lseek`, and old UID syscalls, static `sbrk` state racing with direct `brk`, and errno translation of raw negative values. Test signals are nolibc syscall selftests across architectures, ENOSYS fallback paths, fd lifecycle tests, process creation/wait tests, and filesystem operation round trips in temporary directories.
