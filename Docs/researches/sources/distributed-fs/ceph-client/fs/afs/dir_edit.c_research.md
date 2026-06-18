# sources/distributed-fs/ceph-client/fs/afs/dir_edit.c

Purpose: `dir_edit.c` performs optimistic local modifications to cached AFS directory blobs after successful server mutations, avoiding full refetches when the directory data-version delta is exactly known.

Important APIs and functions: public helpers are `afs_edit_dir_add()`, `afs_edit_dir_remove()`, `afs_edit_dir_update()`, and `afs_mkdir_init_dir()`. Internal helpers manage bitmap and block mechanics: `afs_find_contig_bits()`, `afs_set_contig_bits()`, `afs_clear_contig_bits()`, `afs_dir_get_block()`, `afs_dir_scan_block()`, and `afs_edit_init_block()`.

Control flow: add verifies directory size, maps or allocates blocks, finds contiguous free slots, initializes a new block if needed, writes the dirent, updates bitmaps, allocation counters, hash-chain head, inode version, stats, and dirty state. Remove searches the bucket, clears the entry and slots, fixes the allocation counter and hash-chain predecessor, and marks the inode dirty. Update scans for a name and rewrites vnode/unique fields, mainly for `..` entries on rename. `afs_mkdir_init_dir()` creates `.` and `..` entries in a new directory.

State and persistence: edits modify `vnode->directory`, `directory_size`, inode size, raw i_version, dirty state, and `AFS_VNODE_DIR_VALID`/`AFS_VNODE_DIR_READ`. The caller must hold `validate_lock` and check data-version expectations. Unsafe structure or stale state leads to `afs_invalidate_dir()` rather than a risky edit.

Dependencies and integration points: called by mutation edit hooks in `dir.c` and `dir_silly.c`; depends on AFS XDR directory format, folio queues, netfs allocation, endian helpers, `afs_dir_search_bucket()`, and fscache writeback through dirty marking.

Risks: slot accounting, hash-chain repair, allocation counters, and block-zero reserved slots are all corruption-sensitive. Long multi-slot names, maximum block counts, and concurrent callback invalidation are key edge cases.

Test signals: add/remove head and non-head hash entries, multi-slot names, first directory initialization, block extension, invalid sizes, full directories, callback break during edit, and dirty/version changes.
