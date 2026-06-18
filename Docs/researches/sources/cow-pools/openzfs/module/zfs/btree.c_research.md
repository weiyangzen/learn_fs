# File Research: sources/cow-pools/openzfs/module/zfs/btree.c

## Scope

This file implements OpenZFS's in-kernel/userland generic B-tree container. It covers lifecycle setup, element lookup, insertion, removal, iteration, bulk-insert finishing, destructive traversal, clearing, and optional verification/debug poisoning.

The source was read completely, lines 1-2229.

## Primary APIs And Entry Points

- Module lifecycle: `zfs_btree_init()` creates the default leaf kmem cache, and `zfs_btree_fini()` destroys it.
- Tree lifecycle: `zfs_btree_create()`, `zfs_btree_create_custom()`, `zfs_btree_destroy()`, and `zfs_btree_clear()`.
- Lookup and indexing: `zfs_btree_find()`, `zfs_btree_get()`, `zfs_btree_first()`, `zfs_btree_last()`, `zfs_btree_next()`, and `zfs_btree_prev()`.
- Mutation: `zfs_btree_add()`, `zfs_btree_add_idx()`, `zfs_btree_remove()`, and `zfs_btree_remove_idx()`.
- Destructive iteration: `zfs_btree_destroy_nodes()` lets callers visit all elements while freeing nodes without repeated rebalancing.
- Diagnostics: `zfs_btree_verify()` and helpers validate height, parent pointers, element counts, ordering, and debug poison state depending on `zfs_btree_verify_intensity`.

## Data Model

- `zfs_btree_t` owns comparator callbacks, optional custom in-buffer finder, element size, leaf allocation size, computed leaf capacity, root pointer, height, element/node counts, and a `bt_bulk` pointer used during append-heavy bulk insert mode.
- Every node begins with `zfs_btree_hdr_t`. A core node is identified by `bth_first == -1`; a leaf uses `bth_first` as the starting offset into its element array.
- Core nodes store separator elements plus child pointers. Leaf nodes store actual elements in a movable window so inserts/removes can grow or shrink left or right without always moving the whole leaf.
- Leaves of the default size are allocated from `zfs_btree_leaf_cache`; custom leaf sizes use `kmem_alloc()`. Core nodes are variable sized based on `bt_elem_size`.

## Control Flow

Lookup is a standard B-tree descent. `zfs_btree_find()` walks core separator arrays using `bt_find_in_buf`, then searches the target leaf. During bulk insert mode it first checks the last leaf to optimize mostly increasing insert workloads.

Insertion starts from a caller-provided `zfs_btree_index_t` or a fresh lookup. The first insert allocates a leaf root. Leaf inserts use `bt_grow_leaf()` to make room. If the leaf is full, `zfs_btree_insert_into_leaf()` splits it, chooses a separator, allocates a new leaf, and calls `zfs_btree_insert_into_parent()`. Parent insertion can recursively split core nodes and create a new root.

Bulk insert mode deliberately leaves the final leaf and possibly final ancestors underfull. `zfs_btree_bulk_finish()` fixes those nodes by borrowing from left neighbors and then clears `bt_bulk`.

Removal first replaces core-node deletions with the predecessor from the left subtree so the real removal happens in a leaf. Leaf removal shrinks in place if the node remains above minimum occupancy or is the root. Otherwise it borrows from a left/right sibling or merges nodes, then recursively removes a separator/child from the parent via `zfs_btree_remove_from_node()`.

Iteration uses `first`/`last` subtree helpers and parent traversal. `zfs_btree_next_helper()` is also used by `zfs_btree_destroy_nodes()` with a callback that frees nodes once traversal is finished with them.

Verification is staged by intensity:
- level 1 checks uniform height and node count;
- level 2 checks parent pointers;
- level 3 checks occupancy and total element count;
- level 4 checks strict ordering and separator correctness;
- level 5 checks unused-memory poisoning in debug builds.

## Dependencies

- OpenZFS/SPL allocation and synchronization context: `kmem_cache_*`, `kmem_alloc/free`, `ASSERT`, `VERIFY`, `panic`, and module parameter macros.
- `sys/btree.h` defines the public B-tree structures, capacities, and index types.
- `sys/bitops.h` provides alignment helpers used to compute leaf capacity.
- The comparator function is supplied by callers and must implement strict ordering compatible with the stored element layout.

## Notable Behavior

- `bt_shift_core()` distinguishes parallelogram and trapezoid shifts because core-node elements separate one more child pointer than element in some operations.
- Leaf growth chooses left, right, or both-direction movement based on available headroom and insertion position.
- Removal only borrows from siblings with the same parent. Comments note that borrowing from non-sibling neighbors is not implemented.
- Debug poison uses `0x0f` for unused element bytes and `BTREE_POISON` for unused core child pointers.
- `zfs_btree_destroy_nodes()` invalidates normal B-tree operations until it returns `NULL`; after that, only `zfs_btree_destroy()` is valid.

## Risks And Correctness Notes

- Comparator correctness is critical. Verification level 4 expects adjacent elements to compare exactly `-1`/`1` in the relevant directions, so non-normalized comparators may trip assertions.
- Parent pointer and separator maintenance during split/merge is delicate; errors can make traversal or future updates walk the wrong subtree.
- Bulk mode changes occupancy invariants temporarily, so callers that insert outside the last leaf force `zfs_btree_bulk_finish()` before continuing.
- `zfs_btree_index_t` values can become invalid across structural mutations, especially when finishing bulk mode or deleting elements.
- The implementation assumes element copies with `memcpy`/`memmove` are valid; stored elements must be plain copyable values, not ownership-bearing objects needing constructors/destructors.
- Verification intensity 4 and 5 are intentionally expensive and can become prohibitive for large trees or per-operation debugging.
