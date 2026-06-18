# sources/distributed-fs/ceph-client/tools/include/linux/cache.h

## Purpose

This header supplies minimal cache-line size constants for tools builds.

## APIs, State, and Dependencies

It defines `L1_CACHE_SHIFT` as 5, `L1_CACHE_BYTES` as 32, and `SMP_CACHE_BYTES` as `L1_CACHE_BYTES`. There is no state or dependency.

## Risks and Test Signals

The fixed 32-byte value is a portability approximation and may not match host hardware. Tests are compile-only unless a tool uses these constants for layout or padding, in which case architecture expectations should be reviewed.
