# sources/distributed-fs/ceph-client/fs/btrfs/backref.c

## Purpose
`backref.c` implements Btrfs back-reference discovery and resolution. It answers questions such as "which leaves/inodes/roots reference this logical extent?", "is this data extent shared?", "which paths name this inode?", and "what tree-parent graph should relocation use for this tree block?". The file converts extent-tree references, delayed references, and fs-tree searches into parent logical addresses, inode/file-offset tuples, root IDs, and relocation cache edges.

## Important APIs, types, and functions
- `struct extent_inode_elem` is the private linked-list payload attached to leaf `ulist` entries; each element records inode number, file offset, and referenced byte count for a file extent item.
- `struct preftree`/`struct preftrees` hold merged preliminary refs in cached rbtrees for direct refs, indirect refs with keys, and indirect refs that need keys read from tree blocks.
- `struct share_check` carries state for `btrfs_is_data_extent_shared()`, including target root/inode/bytenr/generation, direct-reference counts, self-reference counts, and whether delayed deletes prevent early exits.
- `btrfs_prelim_ref_init()` and `btrfs_prelim_ref_exit()` create and destroy the `btrfs_prelim_ref` slab cache.
- `btrfs_find_all_leafs()` fills `ctx->refs` with leaves that contain file extent items referencing `ctx->bytenr`.
- `btrfs_find_all_roots()` recursively walks parent refs until root IDs are found in `ctx->roots`.
- `btrfs_is_data_extent_shared()` is the fast sharedness query used by fiemap-like callers.
- `extent_from_logical()`, `iterate_extent_inodes()`, and `iterate_inodes_from_logical()` form the logical-address-to-inode reporting path.
- `btrfs_ref_to_path()`, `paths_from_inode()`, `init_data_container()`, and `init_ipath()` support inode-to-path reporting.
- `btrfs_find_one_extref()` scans `BTRFS_INODE_EXTREF_KEY` items.
- `tree_backref_for_extent()` and the private `get_extent_inline_ref()` iterate inline metadata backrefs in an extent item.
- `btrfs_backref_iter_start()` and `btrfs_backref_iter_next()` provide a metadata-backref iterator over inline and keyed tree refs.
- `btrfs_backref_init_cache()`, node/edge allocation/free helpers, `btrfs_backref_add_tree_node()`, `btrfs_backref_finish_upper_links()`, and `btrfs_backref_error_cleanup()` implement the relocation/general tree-backref cache.

## Control flow
The core walk starts in `find_parent_nodes()`. It chooses the extent root for `ctx->bytenr`, prepares a path against either the commit root or the current tree view, optionally reads delayed refs from an active transaction, then reads inline and keyed extent-tree references. Inline refs are parsed by `add_inline_refs()`, while external keyed refs are collected by `add_keyed_refs()`. Both paths classify direct shared refs, indirect tree refs, indirect data refs, counts, owners, roots, and parent bytenrs into preliminary reference trees.

Indirect refs are resolved in two phases. `add_missing_keys()` reads referenced tree blocks when an on-disk tree-block ref does not carry a search key, inserts a first key into the indirect tree, and releases the extent buffer. `resolve_indirect_refs()` repeatedly removes refs from the indirect tree, calls `resolve_indirect_ref()` to search the owning root, and converts found parents into direct refs. For data refs at level 0, `add_all_parents()` scans matching file extent items, filters by `extent_item_pos` unless ignored, and attaches inode-list data to the leaf parent. Duplicate refs are merged by `prelim_ref_insert()`, which also updates sharedness counters.

After indirect resolution, `find_parent_nodes()` walks the direct-prelim rbtree. Parent bytenrs are appended to `ctx->refs`, roots are appended to `ctx->roots` when a resolved ref has no parent, and missing inode lists for leaf parents are filled by reading the leaf and calling `find_extent_in_eb()`. `btrfs_find_all_leafs()` is a one-level wrapper for data extent to leaf discovery. `btrfs_find_all_roots_safe()` iterates this process, using the `refs` ulist as a frontier until it reaches roots; `btrfs_find_all_roots()` adds `commit_root_sem` protection when there is no transaction.

`iterate_extent_inodes()` resolves a data extent into leaves, then for each leaf either uses caller-provided root cache callbacks or calls `btrfs_find_all_roots_safe()`. For every root/leaf combination, `iterate_leaf_refs()` invokes the supplied `iterate_extent_inodes_t` callback with inode, file offset, byte count, and root ID. `iterate_inodes_from_logical()` first maps an arbitrary logical address to a data extent with `extent_from_logical()`, computes the relative extent item position, and then uses `build_ino_list()` to write triples into a `btrfs_data_container`.

The sharedness query `btrfs_is_data_extent_shared()` first checks a small previous-extents cache, then joins or attaches to a transaction to see delayed refs consistently, or falls back to `commit_root_sem`. It can answer immediately from a path cache when the current leaf is already known shared. Otherwise it calls `find_parent_nodes()` with `share_check`, short-circuiting on direct sharing, different inodes/roots, or known not-shared generation conditions. If direct refs do not prove sharing, it walks up parent tree blocks and stores per-level path-cache answers; multiple parents disable the simple path cache and force conservative invalidation. Results for extents with multiple self refs are stored in the small ring cache.

The path-building path is separate. `paths_from_inode()` searches normal inode refs and extended inode refs, clones the leaf before releasing the shared search path, and calls `inode_to_path()`. `inode_to_path()` stores a pointer into a caller-provided `btrfs_data_container` after `btrfs_ref_to_path()` walks parent inode refs backward into the supplied buffer. Short buffers do not fail; missed paths and missing bytes are counted.

The relocation/general backref cache path uses `btrfs_backref_iter_start()` to locate a metadata extent item, skip data extents, and set cursor pointers for inline or keyed tree refs. `btrfs_backref_add_tree_node()` iterates refs for one tree block. Direct shared block refs call `handle_direct_tree_backref()` and produce an edge to a known parent bytenr or identify a reloc-root self-reference. Indirect tree refs call `handle_indirect_tree_backref()`, which opens the root, searches the commit tree for the child pointer, builds upper nodes/edges along the path, and queues unchecked parents. `btrfs_backref_finish_upper_links()` then inserts the newly checked node and breadth-first finalizes edge membership in upper/lower lists and the cache rb-tree.

## State and persistence behavior
All state is in memory. Walk state lives in caller-owned `struct btrfs_backref_walk_ctx`, temporary `btrfs_path`s, `ulist`s, preliminary ref rbtrees, and linked inode-element lists. There is no new on-disk persistence; the file reads extent-tree items, delayed refs, root tree nodes, file extent items, inode refs, and commit roots to build transient answers.

Consistency depends on the selected view. With a transaction and tree-mod sequence, searches can use old-tree helpers and delayed refs up to `ctx->time_seq`. With `BTRFS_SEQ_LAST`, delayed refs are skipped and commit-root searching is used for qgroup commit-style callers. Without a transaction, `commit_root_sem` protects commit-root views. The sharedness cache stores generation tags from root last-snapshot generation or last root-drop generation so cached not-shared/shared answers are invalidated when snapshots or root drops make them unsafe.

Memory ownership is subtle. `free_leaf_list()` must free inode lists attached to ulist node auxiliary pointers. When preliminary refs are merged or transferred into `ctx->refs`, inode-list ownership is explicitly nulled to avoid double frees. Relocation cache nodes own extent buffers only while cached and locked state requires them; cleanup functions drop locks, extent buffers, rb-tree membership, root refs, and edge lists.

## Dependencies and integration points
The implementation depends on Btrfs extent-tree layout, delayed-ref internals, tree-mod-log sequence handling, root lookup, commit roots, old-tree search helpers, ulist, rbtrees, extent buffers, tree locking, relocation root lookup, simple quota owner refs, and file-item accessors. External users include fiemap/sharedness checks, logical-inode/path ioctls, qgroup/root discovery, send/receive or users of extent inode iteration, and relocation tree-building code.

The file assumes tree-checker and lower Btrfs accessors validate impossible inline-ref types and extent item corruption where possible. It reports corruption with `-EUCLEAN`, missing extents/roots with `-ENOENT`, unsupported metadata iteration cases with `-ENOTSUPP`, and propagates allocation/search errors.

## Risks and test signals
High-risk areas are delayed-ref merging with negative counts, early sharedness exits when delayed deletes exist, tree-mod-log/commit-root view selection, file extent offset underflow compatibility handling, inode-list ownership transfer, cache invalidation around snapshots/root drops, and parent resolution when direct and indirect refs coexist. The relocation cache adds risks around partially built edges, detached nodes, reloc-root self-refs, and cache hits that bypass pending checks.

Useful tests include reflink, snapshot, clone, hole-punch, prealloc, compressed and encoded extents, direct and shared data refs, mixed delayed add/drop refs, deleted roots, qgroup commit-root walks, logical-inode ioctl on exact and ignored offsets, inode path lookup with normal and extended refs, short data containers, skinny and non-skinny metadata, metadata extents with inline and keyed refs, relocation trees, root drop/snapshot generation cache invalidation, and error injection for extent-buffer reads and allocation failures.
