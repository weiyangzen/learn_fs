<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/maple-shared.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/maple-shared.h

## Purpose

`maple-shared.h` sets up shared userspace configuration for maple-tree tests.

## Important APIs, Types, and Functions

It defines `CONFIG_DEBUG_MAPLE_TREE`, `CONFIG_MAPLE_SEARCH`, and `MAPLE_32BIT`, includes `shared.h`, stdlib/time, and `linux/init.h`, declares `maple_rcu_cb()`, remaps `rcu_cb`, and defines `kfree_rcu()` in terms of `call_rcu()` and the maple callback.

## Control Flow and State

The header controls compile-time feature flags and RCU callback routing. Actual free behavior is implemented in `maple-shim.c`.

## Dependencies and Integration Points

It depends on shared kernel-compat headers, maple-tree slot macros, and Userspace RCU. It is included before importing `lib/maple_tree.c`.

## Risks and Test Signals

Risks include configuration drift from kernel maple-tree expectations and incorrect callback container types. Successful maple-tree and VMA tests validate the setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/maple-shared.h -->
