<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/bug.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/bug.h

## Purpose

`linux/bug.h` is a userspace include shim for kernel BUG/WARN support.

## Important APIs, Types, and Functions

It includes `<stdio.h>` and `"asm/bug.h"`, relying on the test include path to provide architecture-specific warning and bug macros.

## Control Flow and State

There is no runtime code in this wrapper.

## Dependencies and Integration Points

It depends on the shared testing include hierarchy and architecture shim headers. It is pulled in by `shared.h` and many kernel data-structure sources compiled in userspace.

## Risks and Test Signals

Risks are missing or incompatible `asm/bug.h` definitions. Successful compilation of shared tests validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/bug.h -->
