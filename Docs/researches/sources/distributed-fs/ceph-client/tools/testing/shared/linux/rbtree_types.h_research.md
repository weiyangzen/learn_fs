<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_types.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_types.h

## Purpose

`linux/rbtree_types.h` exposes kernel rbtree type definitions to userspace test builds.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/rbtree_types.h` with a local guard.

## Control Flow and State

The wrapper has no logic or state.

## Dependencies and Integration Points

It is a dependency for rbtree and interval-tree headers used by shared tests and VMA harness code.

## Risks and Test Signals

The risk is type definition drift or include path failure. Successful shared builds validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rbtree_types.h -->
