<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/idr.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/idr.h

## Purpose

`linux/idr.h` adapts the kernel IDR header for userspace shared tests.

## Important APIs, Types, and Functions

It undefines `__CONCAT` if present to avoid collisions with system headers, then includes `../../../../include/linux/idr.h`.

## Control Flow and State

The wrapper has no runtime logic. IDR behavior comes from imported kernel code and linked generated objects.

## Dependencies and Integration Points

It depends on kernel IDR headers and the shared Makefile's generated `idr.c` from `lib/idr.c`. It integrates IDR with radix-tree and xarray test support.

## Risks and Test Signals

Risks include macro conflicts with libc/system headers and kernel include drift. Successful IDR userspace builds and tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/idr.h -->
