# sources/distributed-fs/ceph-client/include/linux/kho_radix_tree.h

## Purpose

`kho_radix_tree.h` declares the runtime API for a KHO-oriented radix tree that tracks preserved physical pages by PFN and order. It is the non-ABI wrapper around the ABI node layouts from `kho/abi/kexec_handover.h`. The source was read as a complete 70-line file.

## Important APIs, Types, and Functions

`struct kho_radix_tree` contains a root node and a mutex protecting tree structure. `kho_radix_tree_walk_callback_t` receives physical addresses and orders. Public APIs are `kho_radix_add_page()`, `kho_radix_del_page()`, and `kho_radix_walk_tree()`, with `-EOPNOTSUPP` stubs when `CONFIG_KEXEC_HANDOVER` is disabled.

## Control Flow

Client code initializes the root and mutex, adds preserved pages as they are reserved, deletes them when no longer preserved, and walks the tree to emit or consume a memory map. The implementation serializes structural mutation under the embedded mutex.

## State and Persistence Behavior

The tree root and nodes are in kernel memory; the node layout is compatible with KHO preserved-memory ABI. The header owns no allocation logic.

## Dependencies and Integration Points

It depends on errno, mutex types, physical-address types, and the KHO handover core. It integrates with preserved memory tracking before and during kexec.

## Risks and Edge Cases

Callers must initialize the mutex and root correctly. PFN/order encoding must match the ABI constants. Disabled builds return `-EOPNOTSUPP`, so callers must not assume preservation exists.

## Test Signals

Add/delete/walk radix tests, multi-order page coverage, duplicate deletion tests, disabled-config build coverage, and KHO memory-map roundtrip tests are useful.
