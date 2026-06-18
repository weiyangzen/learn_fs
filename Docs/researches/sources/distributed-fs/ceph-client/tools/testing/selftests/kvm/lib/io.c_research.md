# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/io.c

## Purpose
This file provides robust selftest wrappers around `read(2)` and `write(2)` that complete full-count I/O or fail the test with diagnostics.

## Important APIs, Types, and Functions
`test_write()` writes the entire buffer, retrying on `EAGAIN` and `EINTR`, treating short writes as progress, and failing on EOF or unexpected errors. `test_read()` mirrors that behavior for reading exactly the requested byte count.

## Control Flow
Both wrappers loop until `num_written` or `num_read` reaches `count`. `-1` with retryable errno repeats, zero is unexpected EOF, and positive values advance the buffer pointer and remaining length.

## State, Dependencies, and Integration
No state persists beyond loop counters. The wrappers depend on `TEST_ASSERT()` and `TEST_FAIL()` and are used by ELF loading and other file-backed helpers to avoid duplicating short-I/O handling.

## Risks and Test Signals
They assume the caller expects exactly `count` bytes; using them on streams where EOF is valid will fail hard. Successful return always equals requested count, making failures explicit and easy to diagnose.
