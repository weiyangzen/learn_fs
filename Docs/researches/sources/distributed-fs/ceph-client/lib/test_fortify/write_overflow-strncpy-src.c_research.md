
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strncpy-src.c

## Purpose

This test validates `strncpy()` destination overflow when the requested copy length exceeds the destination size.

## Important APIs, Control Flow, And State

`TEST` expands to `strncpy(small, large_src, sizeof(small) + 1)`. The source is large enough, and the explicit count is one byte too large for `small`.

## Dependencies, Risks, And Test Signals

It targets fortified `strncpy()` write-size checks. The expected symbol is `__write_overflow`; the source suffix in the filename distinguishes this scenario from field-specific variants.
