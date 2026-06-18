<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/xarray.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/xarray.h

## Purpose

`linux/xarray.h` adapts the kernel xarray header for userspace tests.

## Important APIs, Types, and Functions

It includes generated `map-shift.h` to set `XA_CHUNK_SHIFT`, then includes `../../../../include/linux/xarray.h`.

## Control Flow and State

No wrapper runtime logic exists. Xarray behavior comes from the kernel header and `xarray-shared.c`.

## Dependencies and Integration Points

It depends on `shared.mk` generating `generated/map-shift.h` and on kernel xarray includes. It integrates with xarray, radix-tree, and idr userspace tests.

## Risks and Test Signals

Risks include stale chunk-shift generation or include path drift. Successful xarray tests across different `SHIFT` settings validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/xarray.h -->
