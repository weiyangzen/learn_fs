# sources/distributed-fs/ceph-client/tools/include/linux/const.h

## Purpose

This header forwards kernel-style constant construction macros to the vdso constant header.

## APIs, State, and Dependencies

It includes `<vdso/const.h>` and defines no additional macros. There is no state or control flow.

## Risks and Test Signals

The include path must provide vdso constants such as `_AC`. Tests are compile-only coverage for headers like `arm-smccc.h` that depend on those macros.
