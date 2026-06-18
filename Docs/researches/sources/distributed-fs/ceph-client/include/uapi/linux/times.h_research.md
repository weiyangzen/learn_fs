# sources/distributed-fs/ceph-client/include/uapi/linux/times.h

## Purpose
Defines `struct tms`, the userspace result for process and children CPU times returned by `times(2)`.

## Important APIs, Types, and Constants
`struct tms` contains `tms_utime`, `tms_stime`, `tms_cutime`, and `tms_cstime`, all `__kernel_clock_t`.

## Control Flow, State, and Persistence
No runtime logic. Kernel snapshots current process and waited-for child CPU accounting into the structure.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Integrates with `times(2)`, libc, shell/accounting tools, and process monitoring.

## Risks and Test Signals
Risks include clock tick unit interpretation and `__kernel_clock_t` size differences. Test syscall results against `/proc` CPU accounting, child accumulation, and 32/64-bit layout.
