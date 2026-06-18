# sources/distributed-fs/ceph-client/fs/jffs2/malloc.c

## Purpose
`malloc.c` centralizes allocation and freeing of JFFS2's frequent in-core objects using slab caches and targeted kmalloc/vmalloc helpers. It covers full dnodes, raw dirents/inodes, temporary dnode info, raw node ref blocks, node fragments, inode caches, and optional xattr objects.

## Important APIs, Types, And Functions
Public functions include `jffs2_create_slab_caches()`, `jffs2_destroy_slab_caches()`, `jffs2_alloc/free_full_dirent()`, `jffs2_alloc/free_full_dnode()`, `jffs2_alloc/free_raw_dirent()`, `jffs2_alloc/free_raw_inode()`, `jffs2_alloc/free_tmp_dnode_info()`, `jffs2_prealloc_raw_node_refs()`, `jffs2_free_refblock()`, `jffs2_alloc/free_node_frag()`, `jffs2_alloc/free_inode_cache()`, and optional xattr alloc/free helpers.

## Control Flow
Module initialization creates all caches, unwinding through `jffs2_destroy_slab_caches()` on failure. Simple alloc/free wrappers call the appropriate cache or kmalloc and emit memory debug traces. Raw-node refs are allocated in blocks of `REFS_PER_BLOCK + 1`, initialized with empty sentinels and a link sentinel. `jffs2_prealloc_raw_node_refs()` ensures an eraseblock has enough empty ref slots before writing nodes.

## State And Persistence Behavior
The file manages only volatile memory, but allocation success is prerequisite for representing persistent raw flash nodes and inode mappings. `jeb->allocated_refs` records reserved ref capacity consumed by later node-linking.

## Dependencies And Integration Points
It depends on kernel slab APIs, `nodelist.h`, debug memory macros, and optional xattr structures. Allocation wrappers are used across scan, readinode, write, dir, erase, and GC code.

## Risks And Test Signals
Partial cache creation must unwind correctly. Raw-ref preallocation must maintain sentinel/link structure or node traversal and erase cleanup break. Tests should inject allocation failures for each cache/object type, stress many node refs per eraseblock, verify no xattr class initialization regressions, and run debug memory tracing during mount/write/GC/unmount cycles.
