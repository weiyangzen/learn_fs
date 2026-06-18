# sources/distributed-fs/ceph-client/include/uapi/linux/time_types.h

## Purpose
Defines kernel UAPI time structures with explicit old and time64 layouts for syscalls and embedded structures.

## Important APIs, Types, and Constants
`struct __kernel_timespec` and `struct __kernel_itimerspec` use 64-bit seconds. Legacy structures include `__kernel_old_timeval`, `__kernel_old_timespec`, and `__kernel_old_itimerval`. `struct __kernel_sock_timeval` uses signed 64-bit seconds and microseconds for socket timeout ABIs.

## Control Flow, State, and Persistence
The header has no runtime logic. It controls ABI layout for old and new time-related syscalls and embedded fields.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Used by taskstats, timer APIs, socket options, and many UAPI headers needing Y2038-safe timestamps.

## Risks and Test Signals
Risks include mixing old and time64 structs, libc conflicts, and padding/alignment differences. Test 32-bit and 64-bit layouts, syscall wrappers using time64, and socket timeout gets/sets.
