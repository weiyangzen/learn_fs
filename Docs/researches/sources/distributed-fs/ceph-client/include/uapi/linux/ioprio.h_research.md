# sources/distributed-fs/ceph-client/include/uapi/linux/ioprio.h

## Purpose
`ioprio.h` defines the packed I/O priority value used by `ioprio_get()` and `ioprio_set()` and interpreted by block schedulers and storage devices.

## Important APIs, Types, and Functions
The ABI is a 16-bit value split into a 3-bit class field, 10-bit hint field, and 3-bit level field. Macros such as `IOPRIO_PRIO_CLASS`, `IOPRIO_PRIO_DATA`, `IOPRIO_PRIO_LEVEL`, and `IOPRIO_PRIO_HINT` extract fields. Classes include none, realtime, best-effort, idle, and invalid. The inline helper `ioprio_value()` validates class, level, and hint and returns the invalid class encoding on bad input. `IOPRIO_PRIO_VALUE` and `IOPRIO_PRIO_VALUE_HINT` build values.

## Control Flow
Userspace composes a priority value, passes it to the ioprio syscall for a process, process group, or user, and the kernel stores it with task or credential-related scheduling state. Block schedulers then consult the packed value when dispatching I/O.

## State and Persistence
The header stores no state. Kernel state persists in task/user I/O-priority settings and may influence future bios. Device duration-limit hints are advisory and only matter when the target stack supports them.

## Dependencies and Integration Points
It includes `<linux/stddef.h>` and `<linux/types.h>`. Integration points are BFQ, mq-deadline, ATA/SCSI command-duration-limit support, and libc/man-page definitions of the ioprio syscalls.

## Risks and Test Signals
Tests should verify packing boundaries, invalid input returning `IOPRIO_CLASS_INVALID`, unchanged semantics for normal best-effort level 4, and scheduler behavior when hints are unsupported. Compatibility risk is mainly bit allocation: class and level widths cannot change without ABI breakage.
