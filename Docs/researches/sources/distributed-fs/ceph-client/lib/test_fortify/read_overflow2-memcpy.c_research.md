
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2-memcpy.c

## Purpose

This negative compile test checks source-side read overflow detection in `memcpy()`.

## Important APIs, Control Flow, And State

The expression is `memcpy(large, instance.buf, sizeof(large))`. The destination can hold 32 bytes, but `instance.buf` is a 16-byte field, so the read side is invalid.

## Dependencies, Risks, And Test Signals

It targets the fortified `memcpy()` wrapper and object-size detection for struct fields. The expected symbol/warning is `__read_overflow2`; lack of detection would permit copying beyond the source field.
