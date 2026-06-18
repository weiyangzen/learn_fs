# sources/distributed-fs/ceph-client/fs/nilfs2/btnode.h

## Purpose
`btnode.h` declares the NILFS B-tree node cache interface and the context object used to move node buffers between cache keys. It is the contract between B-tree, GC, metadata, and inode code and the cache implementation in `btnode.c`.

## Important APIs and types
- `struct nilfs_btnode_chkey_ctxt` carries `oldkey`, `newkey`, current `bh`, and optional prepared `newbh` across prepare/commit/abort.
- `nilfs_init_btnc_inode()` and `nilfs_btnode_cache_clear()` manage the associated cache inode lifecycle.
- `nilfs_btnode_create_block()`, `nilfs_btnode_submit_block()`, and `nilfs_btnode_delete()` provide allocation, read, and invalidation primitives for node buffers.
- `nilfs_btnode_prepare_change_key()`, `nilfs_btnode_commit_change_key()`, and `nilfs_btnode_abort_change_key()` expose the relocation transaction API.

## Control flow and persistence behavior
The header encodes a two-phase mutation contract. Callers prepare a key change before updating DAT or parent pointers, then either commit after persistent metadata is ready or abort to restore cache state. The header does not define on-disk structures; it governs in-memory page-cache state whose dirty buffers are later written by NILFS segment construction.

## Dependencies and integration points
It includes Linux buffer, fs, and backing-device types. `btree.h` embeds `struct nilfs_btnode_chkey_ctxt` in `struct nilfs_btree_path`; `btree.c` uses it for virtual block number replacement and physical assignment; `gcinode.c` uses the submit path for GC node reads; `inode.c` and `mdt.c` attach cache inodes.

## Risks and test signals
Because callers hold relocation state in this struct, stale or reused contexts can corrupt cache keys. Tests should exercise both block-size-equals-page-size and copy fallback modes, abort after prepare failures, and caller paths that update `ctxt->bh` after commit.
