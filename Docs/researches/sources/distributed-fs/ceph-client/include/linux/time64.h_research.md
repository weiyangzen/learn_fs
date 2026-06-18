<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time64.h -->
# sources/distributed-fs/ceph-client/include/linux/time64.h

## Purpose
defines the kernel's 64-bit time scalar/types and inline arithmetic/validation helpers for `timespec64` and `itimerspec64`.

## Important APIs, Types, and Functions
The file is 177 lines and exports these visible symbol families: types/enums `timespec64`, `itimerspec64`, `time64_t`, `timeu64_t`; macros/constants `PSEC_PER_NSEC`, `TIME64_MAX`, `TIME64_MIN`, `KTIME_MAX`, `KTIME_MIN`, `KTIME_SEC_MAX`, `KTIME_SEC_MIN`, `TIME_UPTIME_SEC_MAX`, `TIME_SETTOD_SEC_MAX`; function-like macros none; inline helpers `timespec64_equal`, `timespec64_is_epoch`, `timespec64_compare`, `timespec64_add`, `timespec64_sub`, `timespec64_valid`, `timespec64_valid_strict`, `timespec64_valid_settod`, `timespec64_to_ns`; external prototypes `set_normalized_timespec64`, `ns_to_timespec64`, `timespec64_add_safe`.

## Control Flow
Callers compare, normalize, add, subtract, validate, and convert 64-bit timespecs to/from nanoseconds. Safe add helpers and settimeofday limits protect against overflow and unrealistic wall-clock setting.

## State and Persistence Behavior
No state is stored; the helpers operate on caller-owned time values.

## Dependencies and Integration Points
It depends on kernel time unit constants and 64-bit integer types and is foundational for timekeeping, timers, filesystems, and syscalls. Direct includes are `linux/math64.h`, `vdso/time64.h`, `uapi/linux/time.h`.

## Risks and Edge Cases
Overflow is the key risk: `timespec64_to_ns()` saturates beyond safe ktime limits, and wall-time validation uses stricter settimeofday bounds. Negative nsec or nsec >= NSEC_PER_SEC must be rejected.

## Test Signals
Unit-test normalization, add/subtract, ns conversion saturation, epoch detection, strict and settod validation, and Y2038/ktime boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time64.h -->
