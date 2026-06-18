# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/io_helpers.h

Purpose: declares the timeout-enabled read helper.

Important APIs and functions: `read_with_timeout(int fd, char *buf, size_t count, long usec)`.

Control flow: header only.

State and persistence: none.

Dependencies and integration points: includes unistd for `size_t`/read-related declarations and pairs with `io_helpers.c`.

Risks: function returns negative errno-style `-EAGAIN` for timeout but raw negative `select` errors for select failure, so callers should handle both.

Test signals: compile-time declaration for tests that need bounded blocking reads.
