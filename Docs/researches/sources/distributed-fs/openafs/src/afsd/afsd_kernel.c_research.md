# sources/distributed-fs/openafs/src/afsd/afsd_kernel.c

## Purpose

`afsd_kernel.c` is the native kernel backend for common afsd logic, implementing syscall transport, mount handling, fork/daemon helpers, priority adjustment, mountpoint validation, and the standard `afsd` `main()`.

## Important APIs and Functions

`afsd_init_syscall_opcodes()` builds debug opcode names. `os_syscall()` has platform-specific implementations for Linux, Darwin, Solaris, SGI, AIX, and generic syscall paths. `afsd_call_syscall()` wraps syscall execution and tracing. `afsd_mount_afs()` performs OS-specific mounts and calls `HandleMTab()`. `afsd_fork()`, `afsd_daemon()`, `afsd_check_mount()`, and priority setters satisfy `afsd.h`.

## Control Flow

`main()` initializes unbuffered output, opcode names, command syntax, parses options, handles help, and calls `afsd_run()`. Every common-code AFSOP request reaches `afsd_call_syscall()` and then the selected `os_syscall()`. Mounting is delegated to platform-specific mount/vmount forms and mount-table notification.

## State and Persistence Behavior

Persistent effects include kernel mount state and possible `/etc/mtab` or DiskArbitration updates. Child daemon processes persist after `afsd_fork()` launches callbacks. Debug opcode state is process-local.

## Dependencies and Integration Points

The file depends on OS syscall/mount APIs, OpenAFS syscall devices/opcodes, mount table APIs, POSIX fork/wait/daemon/stat, and `afsd.h`.

## Risks and Test Signals

Risks include platform ABI drift, parameter truncation, direct exit on mount failure, mtab races, and assert-based fork failure handling. Test platform builds, mocked syscall tracing, mountpoint rejection, mtab formatting, help exit status, and startup with mocked kernel syscalls.
