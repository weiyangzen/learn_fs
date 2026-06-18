
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memset.c

## Purpose

This negative build test checks destination-size diagnostics for `memset()`.

## Important APIs, Control Flow, And State

`TEST` is `memset(instance.buf, 0x5A, sizeof(large_src))`, writing 32 bytes into a 16-byte struct field.

## Dependencies, Risks, And Test Signals

It depends on fortified `memset()` size checking. The expected outcome is `__write_overflow` detection in the per-test log.
