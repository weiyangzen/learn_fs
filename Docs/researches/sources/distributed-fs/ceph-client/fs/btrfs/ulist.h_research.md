# sources/distributed-fs/ceph-client/fs/btrfs/ulist.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/ulist.h` declares the Btrfs unique `u64` list container used for iterative graph and tree walks. The file was read as a complete 77-line header for this report.

## Important APIs, Types, and Functions

The header defines `struct ulist_iterator` with a list cursor, `struct ulist_node` with `val`, `aux`, list node, and rb-tree node, and `struct ulist` with node count, list head, rb-root, and one preallocated node. It declares the lifecycle, mutation, deletion, and iteration functions implemented in `ulist.c`.

It also defines `ulist_add_merge_ptr()`, a pointer-friendly inline wrapper around `ulist_add_merge()`. On 32-bit builds it uses an intermediate `u64`; on 64-bit builds it casts the pointer storage directly through the aux pointer.

## Control Flow

There is no standalone runtime flow in the header. Callers initialize or allocate a `ulist`, add values while traversing, initialize an iterator with `ULIST_ITER_INIT()`, repeatedly call `ulist_next()`, and finally release/free the list.

## State and Persistence Behavior

The structs describe volatile in-memory traversal state only. `nnodes` tracks current membership, `nodes` is the iteration list, `root` is the uniqueness index, and `prealloc` is an optional spare node for future insertion.

## Dependencies and Integration Points

The header includes kernel `types`, `list`, and `rbtree` definitions. It is included by Btrfs backref, qgroup, relocation, send, and extent I/O code that needs duplicate suppression for logical addresses, root ids, qgroup ids, or extent ranges.

## Risks and Edge Cases

Callers must not assume internal locking, sorted iteration, or aux replacement on duplicate add. Pointer aux usage must only store pointer values that are valid for the lifetime of traversal. `ULIST_ITER_INIT()` must be called before first iteration, especially when stack-allocated iterators are reused.

## Test Signals

Compile coverage on both 32-bit and 64-bit configurations is useful for the pointer wrapper. Runtime tests should verify that public struct initialization and `ULIST_ITER_INIT()` interoperate with add-during-iteration behavior used by Btrfs graph walks.
