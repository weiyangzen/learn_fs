<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futex2test.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futex2test.h

## Purpose
This header supplies futex2 syscall numbers, flags, structures, and wrappers for futex selftests on systems whose headers may not yet define them.

## Important APIs, Types, And Functions
It defines fallback `__NR_futex_waitv`, `__NR_futex_wake`, `__NR_futex_wait`, `struct futex_waitv`, futex2 flags such as `FUTEX2_SIZE_U32`, `FUTEX2_NUMA`, `FUTEX2_MPOL`, `FUTEX2_PRIVATE`, `FUTEX_32`, `struct futex32_numa`, and wrappers `futex_waitv()`, `futex2_wait()`, and `futex2_wake()`.

## Control Flow
The wrappers call raw syscalls. `futex_waitv()` converts a userspace `timespec` to `struct __kernel_timespec` before passing it with a clock id. `futex2_wait()` and `futex2_wake()` pass full bitsets using `~0U`.

## State And Persistence
The header has no state. Futex state is in caller-provided user memory.

## Dependencies And Integration Points
It integrates futex2 tests with the kernel futex2 ABI and relies on `futextest.h` for `futex_t`.

## Risks
Fallback syscall numbers are architecture-sensitive and may be wrong outside the intended architectures. `futex_waitv()` assumes non-null timeout in its conversion path.

## Test Signals
Futex2 tests compile on old headers and either pass on kernels with futex2 support or fail/skip consistently when syscalls are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futex2test.h -->
