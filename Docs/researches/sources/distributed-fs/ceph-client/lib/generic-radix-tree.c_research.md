# sources/distributed-fs/ceph-client/lib/generic-radix-tree.c

## Purpose
`generic-radix-tree.c` implements the out-of-line pieces of the generic radix tree abstraction: sparse byte-addressed storage with zeroed node allocation, lockless publication through atomic pointer swaps, iteration helpers, preallocation, and destruction.

## Important APIs, Types, and Functions
Exports include `__genradix_ptr()`, `__genradix_ptr_alloc()`, `__genradix_iter_peek()`, `__genradix_iter_peek_prev()`, `__genradix_prealloc()`, and `__genradix_free()`. Internal helpers from the header provide root packing/unpacking, depth sizing, node allocation/free, and inline pointer lookup.

## Control Flow, State, and Persistence
The tree root encodes both node pointer and depth in low bits. `__genradix_ptr_alloc()` first grows the root depth until the requested offset fits, publishing each new root with `cmpxchg_release()`, then descends by depth, allocating and publishing missing child nodes with compare-exchange. Failed races reuse or free the local `new_node`. Iteration peeks walk from the current iterator offset, skipping missing subtrees and adjusting `iter->offset` and `iter->pos`; the reverse variant backs up to the previous allocated page-sized object region. `__genradix_prealloc()` touches each node-sized offset up to `size`, and `__genradix_free()` swaps the root to NULL before recursively freeing nodes.

## Dependencies and Integration Points
It depends on `<linux/generic-radix-tree.h>`, atomic `READ_ONCE`/`cmpxchg_release`/`xchg`, GFP allocation flags, and node helpers defined in the generic radix tree header. Kernel code using `GENRADIX()` typed wrappers maps typed arrays onto these byte-offset primitives.

## Risks and Test Signals
Risks include offset arithmetic near `SIZE_MAX`, iterator progress over sparse holes, concurrent growth races, allocation failure leaving the tree consistent, and `__genradix_free()` assuming a non-NULL root path. Tests should cover sparse high offsets, concurrent allocations to the same and adjacent offsets, forward and reverse iteration over holes, preallocation failure injection, and free-after-populated-tree cleanup.
