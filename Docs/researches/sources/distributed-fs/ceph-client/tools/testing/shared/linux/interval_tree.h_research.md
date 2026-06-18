<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree.h

## Purpose

`linux/interval_tree.h` forwards interval-tree userspace builds to the kernel interval-tree header.

## Important APIs, Types, and Functions

It wraps inclusion of `../../../../include/linux/interval_tree.h` with a local guard `_TEST_INTERVAL_TREE_H`.

## Control Flow and State

No runtime behavior exists in this shim.

## Dependencies and Integration Points

It depends on kernel interval-tree and rbtree headers plus userspace compatibility headers. `interval_tree-shim.c` provides the implementation.

## Risks and Test Signals

Risks include missing kernel dependencies or guard conflicts. Successful interval-tree test builds validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree.h -->
