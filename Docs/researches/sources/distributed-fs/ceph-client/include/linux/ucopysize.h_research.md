# sources/distributed-fs/ceph-client/include/linux/ucopysize.h

## Purpose
Performs object-size sanity checking for usercopy and uio operations, including compile-time overflow diagnostics and optional hardened runtime range validation.

## Important APIs, Types, And Functions
Key APIs are `check_object_size()`, `copy_overflow()`, and `check_copy_size()`. Hardened builds declare `__check_object_size()` and static key `validate_usercopy_range`. Compile-time error hooks are `__bad_copy_from()` and `__bad_copy_to()`, and runtime overflow reporting is `__copy_overflow()`.

## Control Flow
`check_copy_size()` gets the compiler-known object size, rejects copies larger than that object, emits compile-time errors for constant overflows, calls runtime overflow reporting for dynamic overflows, rejects sizes larger than `INT_MAX`, then invokes hardened object-size validation. It returns whether the copy should proceed.

## State, Persistence, And Dependencies
Runtime state is the hardened usercopy static key. Dependencies include bug/WARN infrastructure and jump labels when hardened usercopy is enabled.

## Integration Points
Called by `uaccess.h` and uio copy paths before copying between kernel and user memory.

## Risks And Test Signals
Risks include false negatives when compiler object size is unknown, false positives in flexible-array patterns, disabled hardened validation reducing runtime coverage, and overflows larger than `INT_MAX`. Test signals include compile-time overflow tests, hardened usercopy LKDTM tests, dynamic-size rejection, and builds with hardened usercopy toggled.
