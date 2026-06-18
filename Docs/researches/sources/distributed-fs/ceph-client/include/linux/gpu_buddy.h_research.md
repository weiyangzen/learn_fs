<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpu_buddy.h -->
# sources/distributed-fs/ceph-client/include/linux/gpu_buddy.h

Purpose: This header defines a GPU-oriented binary buddy allocator for managing device address ranges or memory regions with power-of-two block splitting, optional top-down/range allocation, contiguous-only requests, and clear/dirty free trees.

Important APIs/types/functions: Allocation flags include range, top-down, contiguous, clear-preferred, cleared-on-free, and trim-disable. `struct gpu_buddy_block` stores offset, state, clear bit, and order in a packed `header`, tree links, user `private`, and a union of free-tree rb node or allocated-list link. `struct gpu_buddy` stores per-order free red-black trees for clear/dirty blocks, root blocks, root count, max order, chunk size, total size, available bytes, and clear-available bytes. Inline helpers expose block offset, order, free/clear state, and size. Public APIs include init/fini, `gpu_buddy_alloc_blocks()`, trim, reset clear state, free block/list, and print/debug functions.

Control flow, state, and persistence: `gpu_buddy_init()` builds root blocks for the address space. Allocation chooses blocks from rb trees, splits as needed, appends allocated blocks to caller-owned lists, and may trim excess unless disabled. Freeing returns ownership of `link` to the allocator, merges buddies when possible, and accounts clear vs dirty availability. Locking is explicitly caller-owned.

Dependencies/integration: It uses Linux lists, slab allocation, rbtrees, bit operations, and scheduler types. GPU drivers wrap this allocator with their own mutexes and memory object metadata.

Risks and test signals: Header bit packing assumes offsets/order fit masks and chunk size is at least 4 KiB. Missing external locking corrupts rbtrees. Clear/dirty accounting can mislead callers if `GPU_BUDDY_CLEARED` is wrong. Tests should cover non-power-of-two sizes, top-down and ranged allocations, contiguous failures, trimming, merge behavior, clear-tree preference/fallback, reset clear state, and concurrent caller locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpu_buddy.h -->
