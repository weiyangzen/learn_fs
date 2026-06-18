# sources/distributed-fs/ceph-client/arch/um/os-Linux/tty.c

## Purpose
Allocates and prepares host PTY master devices for UML console/terminal use.

## Important APIs, Types, and Functions
`get_pty()` opens `/dev/ptmx`, runs `grantpt()` via `initial_thread_cb()` using `grantpt_cb()`, calls `unlockpt()`, and returns the master fd or negative errno.

## Control Flow, State, and Persistence
No global state. The returned PTY fd persists with the caller; errors close the fd before returning. Running `grantpt()` on the initial thread avoids threading/libc assumptions around PTY permission changes.

## Dependencies and Integration Points
Depends on SKAS initial-thread callback plumbing and host PTY APIs. Used by UML line/console drivers.

## Risks and Test Signals
Risks are missing `/dev/ptmx`, failed grant/unlock, callback deadlocks, and fd leaks. Test console allocation, PTY exhaustion, container PTY permissions, and initial-thread callback behavior.
