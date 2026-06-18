<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_uninitialized_heap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_uninitialized_heap.c

## Purpose
This test checks that waiting on an uninitialized anonymous heap page does not incorrectly block when the expected value does not match zero-filled memory.

## Important APIs, Types, And Functions
It defines globals `child_blocked`, `child_ret`, and `buf`, helper `wait_thread()`, and `TEST(futex_wait_uninitialized_heap)`. It uses `mmap(MAP_PRIVATE|MAP_ANONYMOUS)` and `futex_wait(buf, 1, NULL, 0)`.

## Control Flow
The parent maps a zero-filled page and starts a thread that waits for value `1`. Because the actual value is zero, the futex syscall should immediately return `EWOULDBLOCK`. After a fixed sleep the parent fails if the child is still blocked or reported an unexpected errno.

## State And Persistence
Only anonymous memory and thread flags are used.

## Dependencies And Integration Points
It depends on zero-page handling in futex value comparison, pthreads, mmap, and kselftest harness.

## Risks
There is no `pthread_join()` before test exit. The child status variables are unsynchronized plain globals, which is acceptable for this simple timing test but not a general pattern.

## Test Signals
Pass requires the child to return promptly and accept only `EWOULDBLOCK` for the mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_uninitialized_heap.c -->
