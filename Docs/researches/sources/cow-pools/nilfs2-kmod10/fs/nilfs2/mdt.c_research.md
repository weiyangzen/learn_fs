# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/mdt.c

## Purpose

Implements generic NILFS metadata-file handling: block lookup/creation/deletion, metadata writeback behavior, metadata private state initialization, and shadow-map support for rollback-safe metadata updates.

## Main Responsibilities

- Creates new metadata blocks through bmap insertion and buffer initialization.
- Reads metadata blocks using bmap lookup and buffer-head I/O, with small readahead.
- Provides `nilfs_mdt_get_block()` and `nilfs_mdt_find_block()` as shared metadata block access primitives.
- Deletes metadata blocks, clears dirty state, and invalidates cache pages.
- Implements metadata writeback behavior that redirties folios and triggers segment construction or flushing instead of ordinary block writeback.
- Initializes and destroys `struct nilfs_mdt_info` private state.
- Manages metadata shadow maps used to save/restore bmap and dirty page-cache state.
- Freezes individual buffers into shadow cache and later releases frozen copies.

## Important Functions

- `nilfs_mdt_insert_new_block()` inserts a new bmap entry, zeroes the buffer, optionally calls a block initializer, marks it uptodate/dirty, and marks the metadata inode dirty.
- `nilfs_mdt_create_block()` wraps new-block creation inside a NILFS transaction.
- `nilfs_mdt_submit_block()` grabs a cache buffer, maps it through the metadata bmap, and submits read or readahead I/O.
- `nilfs_mdt_read_block()` performs primary read and optional readahead over adjacent metadata blocks.
- `nilfs_mdt_get_block()` retries read-after-create races when creation returns `-EEXIST`.
- `nilfs_mdt_forget_block()` clears the target buffer state and tries to invalidate the containing folio.
- `nilfs_mdt_write_folio()` redirties metadata folios and triggers segment construction on synchronous writeback or segment flush on reclaim.
- `nilfs_mdt_save_to_shadow_map()` copies dirty metadata pages and btree node pages into shadow inodes and saves bmap state.
- `nilfs_mdt_restore_from_shadow_map()` clears current dirty pages, copies shadow pages back, and restores bmap state under `mi_sem`.
- `nilfs_mdt_clear_shadow_map()` releases frozen buffers and truncates shadow caches.

## Dependencies and Interactions

- Uses `nilfs_grab_buffer()`, `nilfs_copy_dirty_pages()`, `nilfs_copy_back_pages()`, and `nilfs_clear_dirty_pages()` from `page.c`.
- Uses bmap APIs for metadata block mapping.
- Uses `nilfs_iget_for_shadow()` and associated btree-node-cache inodes from `inode.c`.
- Uses allocator-cache hooks from `alloc.h` for persistent allocation metadata.
- Emits tracepoints for metadata block insert and submit operations.

## Notable Behaviors and Edge Cases

- Block sizes larger than `PAGE_SIZE` are explicitly not supported in block initialization/copy paths.
- `nilfs_mdt_submit_block()` returns internal `-EEXIST` when the requested buffer is already uptodate.
- Readahead aborts when bmap lookup fails for a later block.
- Metadata writeback does not write folios directly; it redirties and asks NILFS segment construction to handle persistence.
- Shadow-map restore clears persistent allocator cache if present before copying pages back.
- Frozen buffers are tracked through `b_assoc_buffers` and hold references until explicit release.
