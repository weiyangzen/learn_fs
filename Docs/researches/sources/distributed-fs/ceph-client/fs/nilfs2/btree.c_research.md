# sources/distributed-fs/ceph-client/fs/nilfs2/btree.c

## Purpose
`btree.c` implements NILFS's scalable block-map backend for files and metadata files once direct pointers are insufficient. It stores keyed mappings from file block offsets or node levels to data pointers, supports virtual block numbers through DAT, maintains non-root B-tree nodes in the btnode cache, and supplies normal and GC-specific `nilfs_bmap_operations`.

## Important APIs, types, and functions
- Path management: `nilfs_btree_alloc_path()` initializes per-level buffers, sibling buffers, pointer requests, relocation contexts, and rebalance operation callbacks; `nilfs_btree_free_path()` releases held node buffers.
- Node accessors and mutators read and write `struct nilfs_btree_node` flags, level, child count, keys, and pointers with little-endian conversion.
- Verification helpers `nilfs_btree_node_broken()`, `nilfs_btree_root_broken()`, and exported `nilfs_btree_broken_node_block()` validate node level, root flag, and child-count ranges.
- Lookup paths include `nilfs_btree_do_lookup()`, `nilfs_btree_do_lookup_last()`, `nilfs_btree_lookup()`, `nilfs_btree_lookup_contig()`, `nilfs_btree_seek_key()`, and `nilfs_btree_last_key()`.
- Mutation paths include insert prepare/commit (`nilfs_btree_prepare_insert()`, `nilfs_btree_commit_insert()`), delete prepare/commit (`nilfs_btree_prepare_delete()`, `nilfs_btree_commit_delete()`), rebalance helpers for carry/borrow/split/concat/grow/shrink, and conversion from direct mapping via `nilfs_btree_convert_and_insert()`.
- Persistence callbacks include `nilfs_btree_propagate()`, `nilfs_btree_lookup_dirty_buffers()`, `nilfs_btree_assign()`, `nilfs_btree_mark()`, and GC variants in `nilfs_btree_ops_gc`.
- Public initialization is `nilfs_btree_init()`, `nilfs_btree_init_gc()`, and `nilfs_btree_convert_and_insert()`.

## Control flow
Lookup starts at the root embedded in the inode's bmap data. Each level uses binary search in the current node and follows the selected pointer into the associated btnode cache. At leaf level, `nilfs_btree_lookup_contig()` can translate virtual pointers through DAT and extend the result across physically contiguous blocks, crossing right sibling leaf nodes with readahead.

Insert first looks up the key and expects `-ENOENT`. Prepare allocates a data pointer, then walks from leaf to root to find a node with space, a sibling that can accept entries, or the point where a split/grow is required. It allocates new node blocks and records an operation callback in each path level. Commit walks upward, commits pointer allocations through bmap/DAT, invokes the recorded rebalance operations, dirties affected buffers, and adjusts inode block counts.

Delete looks up the key, prepares end/free operations for each pointer that may be removed, and chooses delete, borrow, concatenate, or shrink operations according to node occupancy. Commit ends DAT/pointer lifetimes, mutates nodes, deletes empty node buffers via `nilfs_btnode_delete()`, and subtracts blocks from inode accounting.

Dirty propagation finds a dirty data or node buffer's key, looks up its ancestors, and either marks parent nodes dirty for physical pointers or performs virtual-pointer replacement with `nilfs_dat_prepare_update()`. For node buffers, DAT updates may require `nilfs_btnode_prepare_change_key()` so the btnode cache key follows the new virtual block number.

Assignment during segment construction converts logical/virtual bmap pointers to newly allocated physical block numbers and fills `union nilfs_binfo` descriptors. Physical mode updates parent pointers and may relocate node cache keys to physical addresses; virtual mode starts DAT entries. GC assignment moves existing DAT mappings with `nilfs_dat_move()`.

## State and persistence behavior
The root node lives inside `nilfs_bmap::b_u.u_data`; non-root nodes live as dirty buffers in the associated btnode cache. Pointers may be physical or virtual depending on bmap type. Virtual pointer lifetimes are managed through DAT prepare/commit/end/update APIs, and written buffers are tagged volatile until assigned to a persistent log address. Dirty node buffers are collected level-ordered so lower-level changes can be propagated before parents are written.

## Dependencies and integration points
The B-tree backend plugs into `struct nilfs_bmap_operations` used by `inode.c`, `direct.c`, `mdt.c`, `segment.c`, and GC paths. It depends on `btnode.c` for non-root node buffers, `dat.c` for virtual block translation/lifetimes, `alloc.c` through bmap pointer allocation wrappers, and inode accounting helpers `nilfs_inode_add_blocks()` and `nilfs_inode_sub_blocks()`.

## Risks and invariants
Node child counts must stay within root/non-root limits, keys must remain sorted, the first key in each child must match promoted parent keys, and every prepared DAT/pointer allocation must be committed or aborted. Corruption is reported as `-EINVAL`/`-EIO` and often clears buffer uptodate state. Internal return codes from btnode reads must be normalized by callers. Split/grow and concat/shrink paths are especially sensitive to sibling buffer ownership and `bp_index` updates.

## Test signals
Strong coverage includes insertion through direct-to-B-tree conversion, root split/grow, sibling carry, deletion with borrow/concat/shrink, contiguous lookups over sibling leaves, virtual block update propagation, node cache key moves, dirty-buffer ordering by level/key, GC assignment/move, and malformed node images with bad level/root/child counts.
