
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memcpy.c

## Purpose

This test validates field-specific destination overflow detection for `memcpy()`.

## Important APIs, Control Flow, And State

`TEST` is `memcpy(instance.buf, large, sizeof(instance.buf) + 1)`. The source can supply the bytes, but the destination field cannot receive them.

## Dependencies, Risks, And Test Signals

The expected diagnostic is `__write_overflow_field`, which is stricter than whole-object bounds. It guards against overwriting adjacent members of `struct fortify_object`.
