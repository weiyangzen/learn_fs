
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memmove.c

## Purpose

This file is the `memmove()` field-destination overflow test.

## Important APIs, Control Flow, And State

`TEST` expands to `memmove(instance.buf, large, sizeof(instance.buf) + 1)`. It writes one byte past `instance.buf` while using a sufficiently large source.

## Dependencies, Risks, And Test Signals

The key expected signal is `__write_overflow_field`. If only whole-object size is considered, this overrun into neighboring struct members could be missed.
