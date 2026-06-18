
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow-memmove.c

## Purpose

This is the `memmove()` destination-overflow equivalent for the fortify test suite.

## Important APIs, Control Flow, And State

`TEST` expands to `memmove(instance.buf, large_src, sizeof(large_src))`. The source has enough bytes, but the destination field is too small.

## Dependencies, Risks, And Test Signals

The target is the fortified `memmove()` wrapper. The build log should confirm `__write_overflow`; otherwise a known oversized move into a field escaped detection.
