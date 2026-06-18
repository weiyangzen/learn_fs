<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/cleanup.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/cleanup.h

## Purpose

`linux/cleanup.h` forwards userspace test builds to the kernel cleanup helper definitions.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/cleanup.h`.

## Control Flow and State

The wrapper contains no runtime logic.

## Dependencies and Integration Points

It depends on the kernel include tree being reachable from tools/testing/shared. It integrates with any imported kernel code that uses cleanup annotations or helpers.

## Risks and Test Signals

Risks include relative include path drift or compiler incompatibility with cleanup attributes. Successful userspace builds are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/cleanup.h -->
