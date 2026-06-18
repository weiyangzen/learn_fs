<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_augmented.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_augmented.h

## Purpose

`linux/rbtree_augmented.h` forwards augmented rbtree helpers to userspace tests.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/rbtree_augmented.h` under a local guard.

## Control Flow and State

There is no runtime code in the wrapper. Augmented callbacks and rotations come from the kernel header.

## Dependencies and Integration Points

It depends on rbtree types and kernel include compatibility. Interval-tree tests rely on augmented rbtree support.

## Risks and Test Signals

Risks include macro incompatibility or missing callback definitions in consumers. Successful interval-tree and rbtree tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_augmented.h -->
