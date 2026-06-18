# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/inode.c

## Purpose

Implements NILFS2 VFS inode operations, address-space operations, inode lifecycle, block mapping, dirty tracking, truncation, attribute updates, permission checks, and FIEMAP reporting.

## Main Responsibilities

- Maps logical file blocks through NILFS bmaps in `nilfs_get_block()`, allocating delayed buffers inside NILFS transactions when `create` is true.
- Defines `nilfs_aops` for read, readahead, writepages, dirty folios, write begin/end, direct I/O reads, invalidation, migration, and partial uptodate checks.
- Creates new inodes through `nilfs_new_inode()`, including ifile allocation, root association, owner initialization, bmap setup, inherited flags, generation number, and inode cache insertion.
- Reads on-disk inode records from ifile via `__nilfs_read_inode()` and initializes VFS operation tables for regular files, directories, symlinks, and special files.
- Provides multiple inode-cache lookup modes: normal mounted-root inodes, GC inodes keyed by checkpoint number, btree-node-cache holder inodes, and shadow inodes.
- Serializes inode metadata back to NILFS on-disk inode format with `nilfs_write_inode_common()` and `nilfs_update_inode()`.
- Truncates bmaps and page cache ranges, evicts deleted inodes, deletes ifile records, and updates root inode/block counters.
- Maintains NILFS dirty-file queues through `nilfs_set_file_dirty()`, `nilfs_inode_dirty()`, and `__nilfs_mark_inode_dirty()`.
- Implements snapshot write protection in `nilfs_permission()`.
- Exposes extent information in `nilfs_fiemap()`, including delayed-allocation extents discovered from folio buffers.

## Important Functions

- `nilfs_get_block()` is the central block mapper used by page-cache read/write paths, FIEMAP, truncation, recovery, and symlink writes.
- `nilfs_write_begin()` / `nilfs_write_end()` wrap generic block write helpers in NILFS transactions and update dirty block accounting.
- `nilfs_dirty_folio()` marks mapped buffers dirty and avoids dirtying holes.
- `nilfs_iget()` and `nilfs_iget_for_gc()` load normal and GC-specific inode views.
- `nilfs_attach_btree_node_cache()` creates an associated inode to hold B-tree node cache pages for a data/metadata inode.
- `nilfs_iget_for_shadow()` creates shadow mapping inodes used by metadata rollback.
- `nilfs_truncate_bmap()` loops from the last mapped key down to the target offset in bounded chunks.
- `nilfs_evict_inode()` handles read-only/purging cases separately from normal deleted-inode cleanup.
- `nilfs_fiemap()` merges contiguous real extents and reports delayed extents as `FIEMAP_EXTENT_DELALLOC`.

## Dependencies and Interactions

- Relies on `nilfs_bmap_*` for logical-to-physical mapping and bmap mutation.
- Uses `ifile` helpers for inode allocation, lookup, mapping, and deletion.
- Uses `page.c` helpers for dirty-buffer counting and delayed extent discovery.
- Uses `segment.h` transaction and segment-construction APIs for synchronous writeback and metadata commits.
- Coordinates with `mdt.c` shadow-map and metadata state via associated btree-node-cache inodes.
- Interfaces with `namei.c` through exported inode operation tables and new inode creation.
- Interfaces with `ioctl.c` GC path through `nilfs_iget_for_gc()`.

## Notable Behaviors and Edge Cases

- Write direct I/O is disabled by returning `0`; direct I/O is only allowed for reads and still needs cleaner synchronization.
- `nilfs_get_block()` allocates a delayed buffer with block number `0` and marks it `new` and `delay`; real disk placement is assigned later by segment construction.
- If concurrent insertion returns `-EEXIST`, it logs a warning and returns `-EAGAIN`.
- Metadata file inodes must be regular files; otherwise read returns corruption/error.
- Inodes with zero link count during iget return `-ESTALE`.
- Snapshot roots (`cno != NILFS_CPTREE_CURRENT_CNO`) reject write permission with `-EROFS`.
- Dirty-file queue insertion uses `igrab()` and can fail if the inode is being freed.
- `__nilfs_mark_inode_dirty()` no-ops while NILFS is purging, preventing writes after log-writer/root teardown.
