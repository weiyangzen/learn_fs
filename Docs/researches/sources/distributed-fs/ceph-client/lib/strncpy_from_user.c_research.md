# sources/distributed-fs/ceph-client/lib/strncpy_from_user.c

## Purpose
Copies a NUL-terminated string from userspace into a kernel buffer with fault handling, object-size checking, and word-at-a-time acceleration. It returns the copied string length excluding the trailing NUL, or a sentinel/error for truncation or faults.

## APIs, Control Flow, and State
The exported API is `strncpy_from_user()`. It calls `might_fault()`, honors fault-injection through `should_fail_usercopy()`, rejects non-positive counts as zero, checks the destination with KASAN and object-size validation, and then chooses masked user access or a normal user access window bounded by `TASK_SIZE_MAX` and `untagged_addr()`. `do_strncpy_from_user()` uses aligned word reads when possible, falls back to byte-at-a-time on unaligned input or user fault, detects NUL with word-at-a-time masks, and clears bytes after the first NUL before writing the final word. If the user count is reached first it returns `count`; if the address-space maximum or fault is hit before the requested count it returns `-EFAULT`.

No persistent state exists; partial destination writes may remain after a fault, as documented.

## Dependencies, Integration, Risks, and Tests
Depends on uaccess access-window helpers, fault-inject-usercopy, KASAN/object-size checking, tagged-address stripping, architecture byte order, and word-at-a-time helpers. Integration points are syscall, procfs, sysfs, ioctl, and BPF-facing paths that need a stable copy of a user string. Risks include callers treating `count` return as success with NUL termination, ignoring partial copies after `-EFAULT`, races where userspace mutates the source during copy, architecture-specific masked access bugs, and failing to size the kernel destination to at least `count`. Test signals include usercopy selftests, KASAN/FORTIFY object-size tests, fault injection, unaligned source/destination tests, page-boundary strings, truncation cases, and BPF map key equivalence tests for post-NUL masking.
