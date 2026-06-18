
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-strcpy-lit.c

## Purpose

This test ensures fortify catches copying an oversized string literal with `strcpy()`.

## Important APIs, Control Flow, And State

`TEST` expands to `strcpy(small, LITERAL_LARGE)`. `small` is 16 bytes and `LITERAL_LARGE` is sized for the larger buffer, making the destination overflow statically visible.

## Dependencies, Risks, And Test Signals

It checks literal-aware string fortify behavior. The expected diagnostic is `__write_overflow`; missing it would weaken common string literal overflow detection.
