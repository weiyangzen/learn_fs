# sources/distributed-fs/ceph-client/samples/seccomp/user-trap.c

## Purpose

This user-space sample demonstrates seccomp user notification. A worker installs a filter that traps `mount(2)` to a listener fd, drops privileges, and a tracer process decides whether to perform bind mounts on its behalf.

## Important APIs, Types, and Functions

Important functions are `seccomp()`, `send_fd()`, `recv_fd()`, `user_trap_syscall()`, `handle_req()`, and `main()`. It uses `SECCOMP_FILTER_FLAG_NEW_LISTENER`, `SECCOMP_RET_USER_NOTIF`, `SECCOMP_IOCTL_NOTIF_RECV`, `SECCOMP_IOCTL_NOTIF_SEND`, `SECCOMP_IOCTL_NOTIF_ID_VALID`, fd passing with `SCM_RIGHTS`, `/proc/<pid>/mem`, and `mount()/umount2()`.

## Control Flow

The parent creates a socketpair and forks a worker. The worker installs a listener-trapping mount filter, drops to uid 1000, sends the listener fd to the parent, attempts a disallowed mount, then attempts an allowed `/tmp/foo` bind mount. The parent forks a tracer, which loops receiving seccomp notifications, validates the trapped syscall, reads source/target strings from the worker's memory after validating notification id, permits only bind mounts where both paths begin `/tmp/`, performs the mount itself, and replies.

## State and Persistence Behavior

State spans three processes: socketpair fd passing, listener fd, notification request/response buffers, `/tmp/foo`, and any successful bind mount. Cleanup kills helper processes, detaches the mount, and removes the directory.

## Dependencies and Integration Points

It depends on modern seccomp user notification APIs, mount permissions in the tracer, `/proc/<pid>/mem`, and local Unix sockets.

## Risks and Edge Cases

The sample explicitly discusses TOCTOU risks and uses `SECCOMP_IOCTL_NOTIF_ID_VALID` after opening task memory. It still has sample-grade string reading and policy. Running it mutates `/tmp/foo` and mount namespace state.

## Test Signals

Run as a user allowed to perform the tracer-side bind mount. The bad mount should fail with `EPERM`, the `/tmp/foo` bind mount should succeed, and cleanup should remove the directory.
