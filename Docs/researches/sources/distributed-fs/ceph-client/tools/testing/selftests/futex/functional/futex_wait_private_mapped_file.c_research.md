<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_private_mapped_file.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_private_mapped_file.c

## Purpose
This regression test targets private file mapping futex key transitions where a mapping may behave like file-backed before write and anonymous after copy-on-write.

## Important APIs, Types, And Functions
It uses global page-aligned padding around `futex_t val`, `wait_timeout`, helper `thr_futex_wait()`, and `TEST(wait_private_mapped_file)`. The futex operations are `futex_wait(&val, 1, timeout, 0)` and `futex_wake(&val, 1, 0)`.

## Control Flow
A thread waits on `val == 1`. The parent sleeps long enough for the waiter to block, changes `val` to `2`, wakes the futex, and expects exactly one waiter found and no timeout.

## State And Persistence
All state is process memory and one pthread.

## Dependencies And Integration Points
It depends on futex key handling for private mappings, pthreads, and kselftest harness.

## Risks
The test relies on a long fixed `WAKE_WAIT_US` sleep. It does not actually create an external file mapping in this source version; the regression signal is tied to the binary's private executable/data mapping layout.

## Test Signals
Pass requires the waiter not timing out and `FUTEX_WAKE` returning `1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_private_mapped_file.c -->
