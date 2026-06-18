# sources/distributed-fs/ceph-client/fs/nilfs2/mdt.c

## Purpose
`mdt.c` implements generic NILFS metadata file services. It provides block read/create/find/delete helpers, metadata writeback behavior, metadata inode initialization/cleanup, entry-size setup, and shadow-map save/restore/freeze support used especially by DAT.

## Important APIs and functions
- Block creation and I/O: `nilfs_mdt_insert_new_block()`, `nilfs_mdt_create_block()`, `nilfs_mdt_submit_block()`, `nilfs_mdt_read_block()`, `nilfs_mdt_get_block()`, and `nilfs_mdt_find_block()`.
- Deletion/cache cleanup: `nilfs_mdt_delete_block()`, `nilfs_mdt_forget_block()`, and `nilfs_mdt_fetch_dirty()`.
- Writeback: `nilfs_mdt_write_folio()`, `nilfs_mdt_writeback()`, and `def_mdt_aops`.
- Lifecycle: `nilfs_mdt_init()`, `nilfs_mdt_clear()`, `nilfs_mdt_destroy()`, and `nilfs_mdt_set_entry_size()`.
- Shadow maps: `nilfs_mdt_setup_shadow_map()`, `nilfs_mdt_save_to_shadow_map()`, `nilfs_mdt_freeze_buffer()`, `nilfs_mdt_get_frozen_buffer()`, `nilfs_mdt_restore_from_shadow_map()`, and `nilfs_mdt_clear_shadow_map()`.

## Control flow
`nilfs_mdt_get_block()` first tries to read an existing metadata block. If the block is absent and creation is allowed, it starts a NILFS transaction, grabs a pagecache buffer, inserts a new bmap entry using the buffer head as the pending pointer, initializes the block, marks it uptodate/dirty, marks the metadata inode dirty, and commits the transaction. If creation races with another insertion, it retries.

Reads submit block I/O by looking up the metadata file bmap for the physical block, mapping the buffer, and optionally issuing up to 15 readahead blocks. `nilfs_mdt_find_block()` uses the bmap seek-key API to skip holes after an initial miss.

Metadata writeback does not flush individual blocks directly in normal operation. It redirties folios and, for synchronous writeback, asks NILFS to construct a segment. If the filesystem is read-only, dirty metadata folios are discarded.

Shadow maps allocate a separate shadow inode plus associated btnode cache. Saving copies dirty metadata pages and dirty btnode pages to the shadow, then saves bmap state. Freezing an individual buffer copies it to the shadow inode and marks the live buffer redirected. Restore clears live dirty pages, copies shadow pages back, restores bmap state, and clears palloc caches if present.

## State and persistence behavior
`struct nilfs_mdt_info` is stored in `inode->i_private` and carries the metadata semaphore, entry sizing, palloc cache pointer, blockgroup lock state, and optional shadow map. Metadata blocks are regular bmap-managed file blocks and are persisted by segment construction. Shadow maps are volatile rollback/consistency state, not durable metadata.

## Dependencies and integration points
The generic layer is used by cpfile, DAT, ifile, sufile, palloc-backed metadata, and B-tree node cache management. It depends on bmap insertion/deletion/lookup, NILFS transactions, segment construction, page copy helpers, palloc cache cleanup, and inode helper `nilfs_iget_for_shadow()`.

## Risks and invariants
Metadata block creation must happen under a transaction and must initialize buffers before marking uptodate. Hole reads return `-ENOENT`, while missing cpfile header blocks are interpreted by callers as corruption. Shadow-map freeze must keep frozen buffers referenced until cleared. `nilfs_mdt_forget_block()` may return `-EBUSY` if dirty state or page invalidation remains. Writeback on read-only filesystems discards dirty metadata, so callers must treat remount-readonly as a corruption/error boundary.

## Test signals
Test metadata block create/read/reread, create races, readahead over holes, find-block range scans, block deletion and page invalidation, dirty fetch from bmap state, sync writeback segment construction, metadata inode cleanup, entry-size calculations, DAT shadow save/freeze/translate/restore/clear, and read-only remount writeback behavior.
