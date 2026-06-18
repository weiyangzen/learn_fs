<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/maple-shim.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/maple-shim.c

## Purpose

`maple-shim.c` imports the kernel maple-tree implementation into userspace and supplies the maple RCU free callback.

## Important APIs, Types, and Functions

It includes `maple-shared.h`, `<linux/slab.h>`, and `../../../lib/maple_tree.c`. `maple_rcu_cb()` converts an `rcu_head` to `struct maple_node` and frees it through `kmem_cache_free(maple_node_cache, node)`.

## Control Flow and State

All maple-tree algorithms come from the included kernel C file. The shim's callback handles delayed node freeing after RCU grace periods. State includes the kernel maple node cache managed by the shared slab stubs.

## Dependencies and Integration Points

It depends on `linux.c` slab emulation, Userspace RCU, and kernel maple-tree source. VMA tests use maple trees as the VMA index.

## Risks and Test Signals

Risks include mismatched `rcu_head` member name, freeing nodes through the wrong cache, or kernel source requiring additional stubs. Maple-tree selftests and sanitizer-enabled VMA tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/maple-shim.c -->
