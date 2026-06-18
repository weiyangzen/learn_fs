<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/rbtree-shim.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/rbtree-shim.c

## Purpose

`rbtree-shim.c` imports the kernel rbtree implementation as a userspace compilation unit.

## Important APIs, Types, and Functions

It includes `../../../lib/rbtree.c`; no additional functions are defined in the shim.

## Control Flow and State

Runtime behavior is entirely from the included kernel source. The shim has no local state.

## Dependencies and Integration Points

It depends on shared rbtree headers and compatibility macros. It supports rbtree, interval-tree, and VMA tests.

## Risks and Test Signals

Risks are include path drift and missing kernel helper stubs. Successful rbtree-dependent test builds validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/rbtree-shim.c -->
