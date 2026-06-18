
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memcpy.c

## Purpose

This test validates destination write-overflow detection for `memcpy()` into a struct field.

## Important APIs, Control Flow, And State

`TEST` is `memcpy(instance.buf, large_src, sizeof(large_src))`. `instance.buf` is 16 bytes and `large_src` is 32 bytes, so the write exceeds the field destination.

## Dependencies, Risks, And Test Signals

The expected fortify symbol is `__write_overflow`. A missed diagnostic would indicate `memcpy()` can overrun a known fixed-size destination.
