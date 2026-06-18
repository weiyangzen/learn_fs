# sources/distributed-fs/ceph-client/lib/radix-tree.h

## Purpose
Declares the radix-tree internals shared with xarray.

## APIs, Control Flow, and State
Forward-declares `struct kmem_cache` and `struct rcu_head`, declares the global `radix_tree_node_cachep`, and declares `radix_tree_node_rcu_free()`. There is no control flow in the header; it exposes node-cache state and RCU freeing for code that must share radix tree node allocation semantics.

## Dependencies, Integration, Risks, and Tests
Used by `radix-tree.c` and xarray-related code needing the same slab cache and RCU cleanup path. Risks include accidental ABI expansion of private helpers, mismatch between node cache lifetime and xarray users, and using the RCU free helper with non-radix nodes. Test signals are build coverage for radix tree plus xarray, boot-time `radix_tree_init()`, and memory debug checks around node free.
