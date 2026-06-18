# sources/distributed-fs/ceph-client/lib/strnlen_user.c

## Purpose
Measures a NUL-terminated userspace string up to a caller-supplied limit, returning a length that includes the trailing NUL. The file explicitly warns that callers should usually prefer copying because userspace can change concurrently.

## APIs, Control Flow, and State
The exported API is `strnlen_user()`. It rejects non-positive counts with zero, then either uses masked user access or starts a normal user read window bounded by `TASK_SIZE_MAX` and `untagged_addr()`. `do_strnlen_user()` aligns the pointer downward, expands the maximum by the alignment offset, masks bytes before the original pointer, then scans word-at-a-time for a zero byte. It returns the length including NUL when found, `count + 1` when the user-supplied limit is hit first, and zero on exception or address-space limit before the requested count.

The function maintains no state and does not stabilize the user string.

## Dependencies, Integration, Risks, and Tests
Depends on uaccess, MM address limits, tagged-address handling, bitops, and word-at-a-time zero detection. Integration points include legacy syscall or proc paths that need to validate approximate user string lengths. Risks include time-of-check/time-of-use races, callers forgetting that too-long is `> count` rather than an errno, zero meaning fault or invalid count, allowed overshoot inside aligned word reads, and reliance on architecture user-access behavior. Test signals include page-boundary tests, invalid pointer faults, masked-access coverage, too-long sentinel cases, count zero/negative cases, and race-aware tests that pair length with a later copy.
