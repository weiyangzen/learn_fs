<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree.h

## Purpose

`linux/rbtree.h` forwards userspace test builds to the kernel rbtree header.

## Important APIs, Types, and Functions

It includes `<linux/kernel.h>` and `../../../../include/linux/rbtree.h` under a local guard.

## Control Flow and State

There is no wrapper logic. Rbtree operations are supplied by kernel headers and `rbtree-shim.c`.

## Dependencies and Integration Points

It depends on the shared `linux/kernel.h` wrapper and kernel rbtree include. It integrates with rbtree, interval tree, and VMA tests.

## Risks and Test Signals

Risks are include drift or missing helper macros. Successful rbtree userspace builds and tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree.h -->
