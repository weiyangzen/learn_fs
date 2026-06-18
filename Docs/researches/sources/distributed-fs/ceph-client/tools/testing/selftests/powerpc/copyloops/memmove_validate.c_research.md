# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memmove_validate.c

## Purpose
Validates a build-selected memmove implementation across overlapping source/destination offsets.

## Important APIs, Types, and Functions
Declares `TEST_MEMMOVE()`, constants `BUF_LEN` and `MAX_OFFSET`, `testcase_run()`, and `main()`.

## Control Flow
`testcase_run()` allocates buffers, initializes patterns, runs the selected memmove across many forward/backward overlap cases, compares against libc/reference expectations, and returns failure on mismatch.

## State and Persistence
Heap buffers are process-local and freed on exit; no persistent state.

## Dependencies and Integration Points
Depends on build-time `TEST_MEMMOVE` macro mapping, malloc, libc memmove/memcmp, and `test_harness()`.

## Risks and Test Signals
Risks include incomplete overlap coverage beyond configured offsets. Failure signal is any mismatched byte pattern.
