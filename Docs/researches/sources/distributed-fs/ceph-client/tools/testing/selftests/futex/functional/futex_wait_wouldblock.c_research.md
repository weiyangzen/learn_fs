<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_wouldblock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_wouldblock.c

## Purpose
This test verifies immediate `EWOULDBLOCK` behavior when classic `futex_wait` and futex2 `waitv` expected values do not match the current futex word.

## Important APIs, Types, And Functions
It defines `TEST(futex_wait_wouldblock)` and `TEST(futex_waitv_wouldblock)`, using `futex_wait()` and `futex_waitv()` with an expected value of `f1 + 1`.

## Control Flow
The classic test uses a short relative timeout but expects immediate `EWOULDBLOCK`. The waitv test computes an absolute monotonic timeout, sets one waiter entry with mismatched value, and also expects immediate `EWOULDBLOCK`.

## State And Persistence
State is local futex words and a local `struct futex_waitv`.

## Dependencies And Integration Points
It depends on futex classic and futex2 value-check semantics and the kselftest harness.

## Risks
The waitv failure checks compare `errno` after `res`, so syscall wrapper conventions must be understood. A kernel that incorrectly waits would make the test timeout or fail.

## Test Signals
Both tests pass only when the syscall returns failure with `errno == EWOULDBLOCK`, not a timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_wouldblock.c -->
