# sources/distributed-fs/ceph-client/fs/xfs/scrub/attr_repair.c

## Purpose
This file repairs an inode's extended attributes by salvaging readable xattr entries from damaged metadata, rebuilding them in a temporary file, and atomically exchanging the rebuilt attr fork into the target inode. It also handles parent pointer filesystems by capturing concurrent dirent updates and replaying them into the temporary attr fork.

## Important APIs, types, and functions
`struct xrep_xattr` is the main repair context, holding tempfile exchange state, `xfarray`/`xfblob` salvage stores, parent pointer replay stores, a dirent hook, and scratch name/value buffers. `xrep_setup_xattr` creates the tempfile and enables dirent gating for parent pointers. Salvage helpers include `xrep_xattr_recover_sf`, `xrep_xattr_recover_leaf`, `xrep_xattr_recover_block`, and local/remote attribute salvage functions. `xrep_xattr_flush_stashed` periodically inserts salvaged attrs into the tempfile. `xrep_xattr_rebuild_tree`, `xrep_xattr_swap`, `xrep_xattr_reset_fork`, and `xrep_xattr_reset_tempfile_fork` commit or clean up forks. `xrep_xattr` is the repair entry point.

## Control flow and state
Repair rejects files without attrs and requires rmapbt plus exchange-range support. It sets up staging arrays, blobs, and optional parent pointer hooks. Shortform attrs are recovered directly from the fork; block-format attrs are scanned by extent mapping, buffer-cache probing, and leaf structure checks. Salvaged attrs are stored as keys plus blob-backed names/values, then flushed to the tempfile to cap memory at roughly eight pages. If parent pointer updates arrive during flushing, repair can reset the tempfile and restart without intermediate flushing. Finalization replays all queued parent pointer changes, prepares local forks for exchange if needed, swaps attr fork mappings, reaps the tempfile's old fork, and invalidates cached ACLs.

## Persistence and integration
The repair crosses several persistence domains: scrub transaction for salvage, ordinary attr transactions for tempfile insertion, atomic extent exchange for final commit, and reap helpers for old attr blocks. Locking deliberately moves between target inode ILOCK/IOLOCK and tempfile locks. Parent pointer updates are observed through `xfs_dir_hook`.

## Risks and test signals
Risks include aliased remote value buffers, live parent pointer update races, duplicate salvaged attrs, partial tempfile resets, and local-to-leaf conversion before exchange. Tests should cover damaged shortform and leaf attrs, corrupt remote value blocks, millions of attrs triggering flushes, parent pointer add/remove during repair, reset/restart after conflict, no-salvage attr fork removal, ACL cache invalidation, exchange failure cleanup, and unsupported-feature returns.
