<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.h

## Purpose

`xarray-shared.h` configures xarray userspace tests.

## Important APIs, Types, and Functions

It defines `XA_DEBUG` and includes `shared.h`.

## Control Flow and State

The header has no runtime flow. Its compile-time state enables xarray debug checks.

## Dependencies and Integration Points

It is included by `xarray-shared.c` before importing `lib/xarray.c`. It depends on the shared compatibility header set.

## Risks and Test Signals

Risks include debug-mode behavior diverging from production or missing compatibility macros. Successful xarray test execution validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/xarray-shared.h -->
