
# sources/distributed-fs/ceph-client/lib/test_fortify/read_overflow2_field-memmove.c

## Purpose

This file validates field-specific source-overread detection in `memmove()`.

## Important APIs, Control Flow, And State

The `TEST` expression is `memmove(large, instance.buf, sizeof(instance.buf) + 1)`. The destination is intentionally large enough so the expected issue is the source field length.

## Dependencies, Risks, And Test Signals

It targets `memmove()` fortify field-size diagnostics. The expected log confirms `__read_overflow2_field`; missed detection would mean field overreads can be hidden by enclosing object size.
