<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.c

## Purpose

`xarray-shared.c` imports the kernel xarray implementation into userspace tests.

## Important APIs, Types, and Functions

It includes `xarray-shared.h` and then `../../../lib/xarray.c`.

## Control Flow and State

All xarray logic and state come from the included kernel source. The wrapper only ensures `XA_DEBUG` and shared compatibility headers are active before inclusion.

## Dependencies and Integration Points

It depends on shared allocation, RCU, radix-tree, and generated map-shift headers from `shared.mk`. It is linked into shared object lists for xarray and related tests.

## Risks and Test Signals

Risks include missing stubs for kernel helpers used by xarray and generated shift mismatches. Successful xarray tests validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.c -->
