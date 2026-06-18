# sources/distributed-fs/ceph-client/include/linux/pid_types.h

## Purpose
Shared PID type enumeration used by task, PID, process group, and session APIs.

## Important APIs, Types, and Functions
Defines `enum pid_type` values `PIDTYPE_PID`, `PIDTYPE_TGID`, `PIDTYPE_PGID`, `PIDTYPE_SID`, and `PIDTYPE_MAX`. Forward-declares `struct pid_namespace` and `init_pid_ns`.

## Control Flow
No runtime flow. The enum selects which PID list or numeric translation a caller wants.

## State and Persistence
No state. The values index arrays such as `struct pid::tasks[PIDTYPE_MAX]`.

## Dependencies and Integration Points
Included by PID and scheduler headers that need the enum without pulling full PID internals.

## Risks
Adding or reordering values affects array indexes and ABI-like internal assumptions. `PIDTYPE_MAX` must remain last.

## Test Signals
Build coverage and PID attach/lookup tests across PID, TGID, PGID, and SID categories.
