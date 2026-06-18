<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time32.h -->
# sources/distributed-fs/ceph-client/include/linux/time32.h

## Purpose
defines legacy 32-bit time structures and conversion helpers for old syscalls and compat paths.

## Important APIs, Types, and Functions
The file is 73 lines and exports these visible symbol families: types/enums `old_itimerspec32`, `old_utimbuf32`, `old_timex32`, `__kernel_timex`; macros/constants none; function-like macros none; inline helpers none; external prototypes `get_old_timespec32`, `put_old_timespec32`, `get_old_itimerspec32`, `put_old_itimerspec32`, `get_old_timex32`, `put_old_timex32`, `ns_to_kernel_old_timeval`.

## Control Flow
Compat syscall code copies old timespec/itimerspec/timex structures from userspace into 64-bit internal forms, performs operations, then copies converted values back.

## State and Persistence Behavior
No state is held here; it is a translation ABI for legacy userspace layouts.

## Dependencies and Integration Points
It depends on old UAPI time structures, `timespec64`, `itimerspec64`, and timex conversion code. Direct includes are `linux/time64.h`, `linux/timex.h`, `vdso/time32.h`.

## Risks and Edge Cases
Y2038 truncation and signed range handling are the core risks. Padding and timeval/timex field differences must not leak or corrupt data.

## Test Signals
Run compat time syscall tests on 32-bit and 64-bit compat kernels, cover boundary dates near 2038, invalid nsec values, and old adjtimex conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time32.h -->
