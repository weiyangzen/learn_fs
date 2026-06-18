# sources/distributed-fs/ceph-client/fs/nilfs2/btnode.c

## Purpose
`btnode.c` implements the page-cache backed buffer cache for non-root NILFS B-tree node blocks. It gives the B-tree code a separate associated inode whose `address_space` stores node buffers keyed by virtual or physical node block number, supports synchronous reads and readahead, and handles node-key relocation when DAT virtual block numbers are replaced or physical addresses are assigned.

## Important APIs, types, and functions
- `nilfs_init_btnc_inode()` formats the associated B-tree-node-cache inode as a regular in-memory cache inode, clears embedded bmap data, applies `GFP_NOFS`, and installs `nilfs_buffer_cache_aops`.
- `nilfs_btnode_cache_clear()` invalidates and truncates all cached node folios.
- `nilfs_btnode_create_block()` allocates a new buffer for a node key, rejects already mapped/uptodate/dirty reuse as metadata corruption, zeroes the block, maps it, and returns a referenced `buffer_head`.
- `nilfs_btnode_submit_block()` obtains a cached buffer, translates virtual block numbers through DAT when needed, submits read or readahead I/O, and returns internal `-EEXIST` for cache hits and `-EBUSY` for skipped readahead.
- `nilfs_btnode_delete()` forgets a node buffer, waits for writeback, clears buffer state, and invalidates the containing page if no dirty buffers remain.
- `nilfs_btnode_prepare_change_key()`, `nilfs_btnode_commit_change_key()`, and `nilfs_btnode_abort_change_key()` implement an atomic-looking cache-key move protocol using `struct nilfs_btnode_chkey_ctxt`.

## Control flow and state behavior
Reads start by grabbing a buffer at the logical node key. If the buffer is already uptodate or dirty, callers receive it without I/O. Otherwise `nilfs_btnode_submit_block()` translates the node key through `nilfs_dat_translate()` for non-DAT inodes when `pblocknr` is not supplied, locks the buffer, submits a read, restores `b_blocknr` to the logical key after submission, and returns the buffer still usable by the cache.

Node relocation is split into prepare/commit/abort. With block size equal to page size, prepare inserts the existing folio into the xarray at `newkey` and keeps it locked while its `folio->index` still names `oldkey`; commit erases `oldkey`, marks `newkey` dirty, updates `folio->index` and `bh->b_blocknr`, then unlocks. If xarray insertion conflicts or block and page sizes differ, prepare creates a new buffer at `newkey`; commit copies buffer contents and state from old to new and deletes the old buffer. Abort removes the prepared xarray entry or deletes the newly created buffer.

## Dependencies and integration points
The file depends on `nilfs_grab_buffer()`, `nilfs_forget_buffer()`, `nilfs_copy_buffer()`, `nilfs_buffer_cache_aops`, DAT translation, and folio/xarray primitives. It is called from `btree.c`, `gcinode.c`, `inode.c`, `mdt.c`, and cleanup paths that attach or clear B-tree node caches.

## Risks and invariants
The most important invariant is that cache keys, buffer `b_blocknr`, and folio indices must not diverge except during the locked prepare/commit window. Reusing a mapped, uptodate, or dirty buffer for a supposedly new node is treated as corruption. Readahead uses internal return codes, so callers must not expose `-EEXIST` or `-EBUSY` as user-visible failures without conversion. The implementation explicitly does not support folio sizes larger than the page size for full-folio key moves.

## Test signals
Useful signals include B-tree insert/delete/grow/shrink tests with node allocation, DAT virtual-block update tests that force node key changes, GC reads of node blocks, metadata corruption tests that duplicate node addresses, readahead cache-hit paths, and error injection around `nilfs_dat_translate()`, xarray insertion, and `nilfs_btnode_create_block()`.
