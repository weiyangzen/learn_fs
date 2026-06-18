# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/errno-base.h

## Purpose
Defines the base POSIX/Linux errno values 1 through 34 for generic UAPI consumers.

## Important APIs, Types, and Functions
Exports constants such as `EPERM`, `ENOENT`, `EINTR`, `EIO`, `EAGAIN`, `ENOMEM`, `EACCES`, `EINVAL`, `ENOSPC`, `EPIPE`, `EDOM`, and `ERANGE`.

## Control Flow, State, and Persistence
This is a pure constant header with no runtime behavior or state.

## Dependencies and Integration
No includes. It is included by `asm-generic/errno.h` and by architecture errno wrappers that use generic Linux errno numbering.

## Risks and Test Signals
Risks are ABI breakage if numeric values change and collisions with libc errno definitions when include ordering is wrong. Test signals include preprocessing alongside libc headers and asserting key errno numeric values against Linux UAPI expectations.
