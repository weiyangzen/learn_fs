<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_waitv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_waitv.c

## Purpose
This test covers futex2 `futex_waitv()` waiting on multiple futexes, for private and shared futex arrays plus invalid-argument cases.

## Important APIs, Types, And Functions
It uses global `waitv[NR_FUTEXES]`, `futexes[NR_FUTEXES]`, helper `waiterfn()`, and tests `private_waitv`, `shared_waitv`, `invalid_flag`, `unaligned_address`, `null_address`, and `invalid_clockid`. It calls `futex_waitv()` and wakes with classic `futex_wake()` on the final futex.

## Control Flow
The private test points all waitv entries at local futexes with `FUTEX_32|FUTEX_PRIVATE_FLAG`, starts a waiter, then wakes the last futex and expects `futex_waitv()` to return that index. The shared test uses SysV shared memory entries with shared flags. Invalid tests mutate flags, address, pointer, or clockid and expect syscall rejection.

## State And Persistence
It uses process memory, SysV shared memory attachments, one waiter thread per positive case, and global waitv entries reused by tests.

## Dependencies And Integration Points
It depends on the `futex_waitv` syscall, classic futex wake compatibility, SysV shared memory, and kselftest harness.

## Risks
Several invalid tests appear to check `res == EINVAL` rather than `res < 0 && errno == EINVAL`, which may weaken failure detection. SysV segments are detached but not explicitly removed. Positive tests rely on a fixed sleep before wake.

## Test Signals
Positive signals are wake return `1` and waiter return index `NR_FUTEXES - 1`; invalid cases should surface `EINVAL`-class behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_waitv.c -->
