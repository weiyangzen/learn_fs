
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strscpy.c

## Purpose

This test checks destination overflow detection for the kernel `strscpy()` helper.

## Important APIs, Control Flow, And State

`TEST` expands to `strscpy(instance.buf, large_src, sizeof(instance.buf) + 1)`. The specified destination size exceeds the actual field size by one byte.

## Dependencies, Risks, And Test Signals

It validates that `strscpy()` participates in fortify destination-size checking. The expected signal is `__write_overflow` in the compile log.
