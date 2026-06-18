# sources/distributed-fs/openafs/src/afs/UKERNEL/afsd_uafs.c

## Purpose

`afsd_uafs.c` adapts the afsd cache-manager startup interface to the UKERNEL/libuafs environment. It supplies afsd callbacks that would normally mount, fork, daemonize, or make syscalls in a kernel-backed client.

## Important APIs, Types, and Functions

- `afsd_mount_afs` sets the libuafs mount directory and calls `uafs_mount`.
- `afsd_set_rx_rtpri` and `afsd_set_afsd_rtpri` are no-op priority hooks.
- `afsd_check_mount` accepts the mount point without host validation.
- `afsd_call_syscall` packages `struct afsd_syscall_args` through `call_syscall(AFSCALL_CALL, ...)`.
- `afsd_fork` starts an afsd callback on a pthread with `usr_thread_create`, then joins or detaches depending on `wait`.
- `afsd_daemon` is a no-op and returns success.

## Control Flow

The afsd runtime calls these hooks during `uafs_Run`/`afsd_run`. Instead of kernel syscalls and process forks, the code stays in-process: mount requests go through libuafs globals, syscall requests go through the UKERNEL `Afs_syscall` shim, and daemon workers become pthreads.

## State and Persistence Behavior

This file keeps no persistent state. It mutates libuafs mount state through `uafs_setMountDir` and `uafs_mount`; thread lifetimes are controlled by join/detach behavior.

## Dependencies and Integration Points

It depends on `afs/sysincludes.h`, `afsincludes.h`, `afs_usrops.h`, afsd headers, and `afs_args.h`. It is only compiled under `UKERNEL`.

## Risks and Edge Cases

`afsd_check_mount` always returns success, so invalid mount names must already be handled in `uafs_setMountDir`. `afsd_fork` reports raw pthread return codes rather than errno-style transformed errors. Daemonization and priority knobs are intentionally ignored, which can affect callers expecting process isolation or scheduling changes.

## Test Signals

Exercise afsd startup under libuafs with both waiting and detached callback threads. Verify mount-dir changes take effect, syscall arguments reach `Afs_syscall`, and daemon/priority calls do not fail startup.
