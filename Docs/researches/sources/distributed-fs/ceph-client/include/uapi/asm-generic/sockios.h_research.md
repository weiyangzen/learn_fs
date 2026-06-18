# sources/distributed-fs/ceph-client/include/uapi/asm-generic/sockios.h

## Purpose
Provides generic socket-level ioctl command numbers.

## Important APIs, Types, And Functions
Exports `FIOSETOWN`, `SIOCSPGRP`, `FIOGETOWN`, `SIOCGPGRP`, `SIOCATMARK`, `SIOCGSTAMP_OLD`, and `SIOCGSTAMPNS_OLD`.

## Control Flow
No runtime or compile-time branching beyond the include guard.

## State, Persistence, And Dependencies
No state. The constants address socket ownership, process-group signaling, out-of-band mark detection, and old timeval/timespec timestamp reads in the socket layer.

## Integration Points
Included by architecture `asm/sockios.h` and indirectly by socket headers. Used by `ioctl(2)` on sockets and compatibility paths that still expose old timestamp commands.

## Risks
These hexadecimal ioctl values are ABI. Old timestamp commands are time-size-sensitive and must remain distinct from newer time64 mechanisms.

## Test Signals
Socket `ioctl` tests for owner and process group, `SIOCATMARK` tests with urgent data, and compat timestamp tests on 32-bit user space.
