<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sched/types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sched/types.h

Purpose: defines the extensible `sched_attr` structure used by `sched_setattr` and `sched_getattr` to pass scheduler policy, realtime priority, deadline parameters, and utilization hints.

Important APIs, types, and functions: `SCHED_ATTR_SIZE_VER0` and `SCHED_ATTR_SIZE_VER1` record ABI growth. `struct sched_attr` includes `size`, `sched_policy`, `sched_flags`, nice value, realtime priority, deadline runtime/deadline/period, and utilization clamp min/max.

Control flow: userspace fills `sched_attr` with a size value and calls scheduler attribute syscalls. The kernel copies only the advertised size, validates flags and fields for the selected policy, applies scheduling-class parameters, and reports supported fields through `sched_getattr`.

State and persistence behavior: task scheduling state persists in kernel task structures until changed or reset on fork according to flags. The struct is a transient syscall payload.

Dependencies and integration points: depends on `linux/types.h` and integrates with `sched.h` policy/flag constants, deadline scheduling, realtime scheduling, CFS nice values, and utilization clamping.

Risks and edge cases: ABI extension requires append-only fields and correct `size` handling. Utilization hints use scheduler capacity units and can be reset with special values documented outside the struct. Deadline fields need nonzero and ordered runtime/deadline/period validation.

Test signals: sched_setattr/getattr selftests for every size version, deadline policy boundary checks, utilization clamp flags, reset-on-fork behavior, and invalid size/flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sched/types.h -->
