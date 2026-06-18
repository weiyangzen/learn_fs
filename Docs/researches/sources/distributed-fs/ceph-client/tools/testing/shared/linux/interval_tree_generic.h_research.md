<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree_generic.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree_generic.h

## Purpose

`linux/interval_tree_generic.h` forwards generic interval-tree macro definitions into userspace tests.

## Important APIs, Types, and Functions

It includes `../../../../include/linux/interval_tree_generic.h`.

## Control Flow and State

There is no independent logic; generated interval tree operations come from the included kernel macros.

## Dependencies and Integration Points

It depends on the kernel include tree and the rbtree compatibility environment. It is included indirectly by interval-tree userspace tests.

## Risks and Test Signals

Risks are include path drift and macro incompatibilities with userspace compilation. Successful interval-tree builds are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/interval_tree_generic.h -->
