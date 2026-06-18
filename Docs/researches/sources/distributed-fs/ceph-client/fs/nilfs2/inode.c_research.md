# sources/distributed-fs/ceph-client/fs/nilfs2/inode.c

## Purpose
`inode.c` implements NILFS inode lifecycle, address_space operations, block lookup/allocation, dirty tracking, truncation, eviction, raw inode serialization, permission checks, and fiemap reporting.

## Important APIs and functions
- Block mapping and I/O: `nilfs_get_block()`, `nilfs_read_folio()`, `nilfs_readahead()`, `nilfs_writepages()`, `nilfs_dirty_folio()`, `nilfs_write_begin()`, `nilfs_write_end()`, and read-only `nilfs_direct_IO()`.
- Inode lifecycle: `nilfs_new_inode()`, `nilfs_iget_locked()`, `nilfs_iget()`, `nilfs_ilookup()`, `nilfs_iget_for_gc()`, `nilfs_attach_btree_node_cache()`, `nilfs_detach_btree_node_cache()`, and `nilfs_iget_for_shadow()`.
- Raw inode conversion: `nilfs_read_inode_common()`, `nilfs_write_inode_common()`, `nilfs_update_inode()`, and `nilfs_load_inode_block()`.
- Cleanup/mutation: `nilfs_truncate()`, `nilfs_evict_inode()`, `nilfs_setattr()`, `nilfs_permission()`, `nilfs_inode_dirty()`, `nilfs_set_file_dirty()`, `__nilfs_mark_inode_dirty()`, `nilfs_dirty_inode()`, and `nilfs_fiemap()`.
- Exported address-space operation tables include `nilfs_aops` and `nilfs_buffer_cache_aops`.

## Control flow
`nilfs_get_block()` first performs a contiguous bmap lookup under the DAT metadata semaphore. On a hit it maps the buffer and may enlarge `bh_result->b_size` to the contiguous run. On a missing block with create set, it begins a NILFS transaction, inserts a delayed/volatile bmap entry using the caller's buffer head, marks the inode dirty synchronously, commits, and marks the buffer new, delayed, and mapped to block zero until segment assignment supplies a real address.

Buffered writes begin a transaction before `block_write_begin()` and commit after `generic_write_end()` plus dirty-block accounting. Writeback does not write pages directly; synchronous writeback constructs a data-sync segment. Dirty folios mark mapped buffers dirty and increment NILFS dirty-block counters.

Inode lookup uses `iget5_locked()` with a key containing inode number, root, checkpoint number, and inode type. Normal inodes read raw entries from the root ifile, initialize file/dir/symlink/special operation tables, read bmaps for regular/dir/symlink files, and apply inode flags. GC and shadow inodes use special types and in-memory initialization.

Creation allocates an ifile entry, initializes ownership/times/flags/generation, reads an empty bmap for regular/dir/symlink, inserts into the inode cache, and leaves cleanup to eviction on later failure. Eviction truncates pagecache and bmap, deletes the ifile entry, decrements root inode counts, and respects read-only or writer-detached states by avoiding writes.

Fiemap merges committed physical extents from bmap lookups with delayed allocation extents from `nilfs_find_uncommitted_extent()`, marking delalloc extents with `FIEMAP_EXTENT_DELALLOC`.

## State and persistence behavior
In-memory `struct nilfs_inode_info` holds root, dirty-list state, bmap, associated btnode cache, raw inode buffer, flags, checkpoint number, and inode type. Persistent state is raw `struct nilfs_inode` entries in ifile plus bmap data written separately. Dirty files are queued on `nilfs->ns_dirty_files`, dirty block counts update `ns_ndirtyblks`, and segment construction later assigns physical blocks and writes inode/bmap state.

## Dependencies and integration points
The file depends on bmap backends (`direct.c`, `btree.c`), ifile allocation, cpfile root loading, metadata semaphores, segment construction, page helpers, ACL/namei operation tables outside this work item, and ioctl/file operation hooks. It provides functions used by directory, file, metadata, DAT, B-tree, and GC code.

## Risks and invariants
Snapshot roots are read-only for write permission. DAT semaphores must protect virtual block lookups. `nilfs_get_block()` races on insertion are converted to `-EAGAIN` with a warning. Dirty-list state bits must stay consistent with inode references to avoid use-after-free or leaked dirty inodes. `nilfs_iget_for_shadow()` appears to return the original inode instead of `s_inode` when an existing shadow inode is found, which is a code path worth scrutiny. Truncation ignores return values from segment construction because VFS truncate has no return channel.

## Test signals
Test buffered read/write allocation, direct I/O reads, mmap and writeback interaction, inode create/failure/evict, bmap truncation in chunks, snapshot write denial, dirty-list queueing under concurrency, raw inode serialization, btnode cache attach/detach, shadow inode setup, and fiemap with committed plus delayed extents.
