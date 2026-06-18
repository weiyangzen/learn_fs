# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-read.c

## Purpose
Implements AFR directory open, read, read-plus, and release operations. It keeps directory fds open on all currently usable replica children, selects one readable replica for `readdir`/`readdirp`, and hides AFR-private implementation entries from root listings.

## Important APIs, types, and functions
`afr_opendir()` initializes `afr_local_t`, checks quorum/consistent I/O, gets `afr_fd_ctx_t`, and fans out `opendir` to every up child. `afr_opendir_cbk()` records per-child replies and `fd_ctx->opened_on[]`. `afr_do_readdir()` is shared by `afr_readdir()` and `afr_readdirp()`. `afr_readdir_wind()` stores `fd_ctx->readdir_subvol` and winds the selected child FOP. `afr_readdir_transform_entries()` moves entries into the caller list, skips private dirs, and invalidates entry inodes whose cached readable subvol is not compatible with the parent read child.

## Control flow
First directory read, or any read without a pinned child, enters `afr_read_txn()` with an `AFR_DATA_TRANSACTION`. A failed offset-zero read can call `afr_read_txn_continue()` and fail over. Later reads with nonzero offset bypass read selection and reuse `fd_ctx->readdir_subvol`, preserving directory offset semantics.

## State and persistence behavior
State is transient except for fd context: `opened_on[]` tracks which children have an open fd and `readdir_subvol` pins offset continuation. No on-disk data is changed. Entry inode references from `readdirp` are dropped when validation shows they could represent stale metadata.

## Dependencies and integration points
Depends on `afr-transaction.h`, AFR read-subvolume helpers, inode refresh/readable caches, Gluster list and dict APIs, child xlator directory FOPs, and `afr_cleanup_fd_ctx()` on release.

## Risks and test signals
Risks include incorrect offset failover, stale `readdirp` inodes when healing or consistent metadata is enabled, fd context allocation failures, private directory leakage from root, and quorum edge cases. Tests should cover first-read failover, continued reads staying pinned, private directory filtering, readdirp inode invalidation after generation changes, and all-children-down/quorum failures.
