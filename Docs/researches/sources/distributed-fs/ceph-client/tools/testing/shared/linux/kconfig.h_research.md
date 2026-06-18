<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kconfig.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/kconfig.h

## Purpose

`linux/kconfig.h` forwards Kconfig helper macros for userspace test builds.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/kconfig.h`.

## Control Flow and State

There is no runtime behavior.

## Dependencies and Integration Points

It lets imported kernel headers use `IS_ENABLED()` and related Kconfig macros in userspace.

## Risks and Test Signals

Risks include relative include path drift or missing generated config macros. Successful shared-test compilation validates the shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/kconfig.h -->
