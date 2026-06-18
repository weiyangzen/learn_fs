# Group Research: group_805_linux_sources_os_linux_linux_fs_ntfs3_file_c_sources_os_linux_linux__217002cfb714

Scope: `Docs/research_subset_a.md` only.  
Read status: all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/file.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/file.c

## Purpose

Implements regular-file VFS operations for the Linux `ntfs3` driver. This file is the user-facing I/O layer for NTFS files: open, read, write, mmap, fallocate, truncate/extend, fsync, fiemap, ioctl, splice, llseek, and file attributes.

## Main Interfaces

- `ntfs_file_operations`: wires `.read_iter`, `.write_iter`, `.mmap_prepare`, `.open`, `.release`, `.fsync`, `.fallocate`, `.splice_read`, `.splice_write`, `.llseek`, and ioctls.
- `ntfs_file_inode_operations`: wires getattr/setattr, ACL, xattr listing, fiemap, and fileattr retrieval.
- `ntfs_ioctl()` supports `FITRIM`, filesystem label get/set, and `NTFS3_IOC_SHUTDOWN`.
- `ntfs_getattr()` reports NTFS birth time, cluster block size, immutable/append/compressed/encrypted statx attributes.
- `ntfs_setattr()` handles size changes, chmod ACL updates, readonly flag synchronization, and WSL permission persistence.

## Key Behavior

- Direct I/O is attempted only when the inode supports it and position plus iterator alignment match `sbi->bdev_blocksize`; otherwise I/O falls back to buffered paths.
- Reads reject bad inodes, forced-shutdown filesystems, encrypted files, unsupported external compression builds, and deduplicated files.
- Writes reject bad inodes, forced shutdown, encrypted files, deduplicated files, immutable files, and direct I/O to compressed files.
- Compressed native NTFS writes go through `ntfs_compress_write()`, which works frame-by-frame, fills gaps between valid size and write position, reads partial frames when needed, then calls `ni_write_frame()`.
- mmap rejects encrypted and deduplicated files. Writable mmap of compressed files is unsupported. Writable mmap of sparse files preallocates clusters and extends initialized size before mapping.
- `ntfs_filemap_close()` advances `ni->i_valid` for writable mappings whose mapped range was extended.
- `ntfs_extend()` grows file size, marks the volume dirty, extends initialized size through iomap zeroing when needed, updates times, and performs synchronous writeback for sync inodes.
- `ntfs_truncate()` updates page cache size, calls `attr_set_size_ex()`, updates `ni->i_valid`, sets archive bit, and synchronizes for dirsync inodes.
- `ntfs_fallocate()` supports normal preallocation, `KEEP_SIZE`, `PUNCH_HOLE`, `COLLAPSE_RANGE`, and `INSERT_RANGE` with different behavior for sparse/compressed-capable files. It serializes with direct I/O and page-cache invalidation for range surgery.
- `ntfs_file_release()` allocates delayed-allocation clusters on last writer close and removes preallocation when the mount option requests it.
- `ntfs_file_fsync()` flushes file data, inode metadata, parent directory duplicate metadata, clears NTFS dirty state, updates MFT mirror, syncs the block device, and issues a flush.

## Dependencies

- VFS/iomap/page-cache APIs: `generic_file_read_iter`, `iomap_dio_rw`, `iomap_file_buffered_write`, `iomap_zero_range`, `iomap_fiemap`, `filemap_*`.
- NTFS attribute/run helpers: `ntfs_set_size`, `attr_set_size[_ex]`, `attr_data_get_block`, `attr_punch_hole`, `attr_collapse_range`, `attr_insert_range`, `attr_force_nonresident`.
- NTFS inode helpers from `frecord.c`: `ni_allocate_da_blocks`, `ni_read_frame`, `ni_write_frame`, `ni_decompress_file`, `ni_seek_data_or_hole`, `ni_write_parents`.
- Filesystem state helpers: `ntfs_set_state`, `ntfs_trim_fs`, `ntfs_set_label`, `ntfs_update_mftmirr`.

## Error and Safety Notes

- Most public entry points guard `is_bad_ni()` and forced shutdown.
- Privileged ioctls require `CAP_SYS_ADMIN`.
- Unsupported encrypted/deduplicated paths return `-EOPNOTSUPP`, not partial behavior.
- Direct I/O is explicitly incompatible with delayed allocation; delayed blocks are forced before DIO.
- External compressed files are decompressed on write/open with `CONFIG_NTFS3_LZX_XPRESS`; otherwise write access is rejected.
- `ntfs_fallocate()` is the highest-risk path in this file because it combines page-cache invalidation, range mutation, allocation, sparse/compressed distinctions, and size/valid-size updates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/frecord.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/frecord.c

## Purpose

Implements NTFS file-record (`MFT_REC`) management for `ntfs3`. It presents a coherent `ntfs_inode` view across the base MFT record, external subrecords, attribute-list entries, resident/nonresident attributes, names, compression frames, parent-directory duplicate metadata, dirty writes, and delayed allocation.

## Main Interfaces

- MFT/subrecord lifecycle: `ni_load_mi_ex()`, `ni_load_mi()`, `ni_load_all_mi()`, `ni_add_subrecord()`, `ni_remove_mi()`, `ni_clear()`.
- Attribute discovery/enumeration: `ni_find_attr()`, `ni_enum_attr_ex()`, `ni_std()`, `ni_std5()`.
- Attribute mutation: `ni_insert_resident()`, `ni_insert_nonresident()`, `ni_remove_attr()`, `ni_remove_attr_le()`, `ni_new_attr_flags()`.
- Attribute-list management: `ni_create_attr_list()`, `ni_expand_list()`, internal `ni_try_remove_attr_list()`, `ni_ins_attr_ext()`.
- File deletion: `ni_delete_all()`.
- Names and rename: `ni_fname_name()`, `ni_fname_type()`, `ni_add_name()`, `ni_remove_name()`, `ni_remove_name_undo()`, `ni_rename()`.
- Compression: `ni_parse_reparse()`, `ni_read_folio_cmpr()`, `ni_read_frame()`, `ni_write_frame()`, and, with `CONFIG_NTFS3_LZX_XPRESS`, `ni_decompress_file()`.
- Writeback: `ni_is_dirty()`, `ni_write_inode()`, `ni_write_parents()`.
- Delayed allocation: `ni_allocate_da_blocks()`, `ni_allocate_da_blocks_locked()`.
- Seeking: `ni_seek_data_or_hole()`.

## Key Behavior

- Subrecords are cached in `ni->mi_tree`, keyed by record number, and loaded lazily through attribute-list entries.
- `ni_find_attr()` chooses the base record fast path when there is no attribute list, otherwise resolves the list entry, loads the containing subrecord, validates VCN coverage, and marks the inode bad on inconsistencies.
- Attribute insertion prefers the base record, creates an attribute list when required, and spills eligible attributes into external records when the base record lacks space.
- `$MFT::$DATA` has special handling: its first data segment must remain in the base record, so other attributes may be moved out to make room.
- Attribute-list shrink/removal is attempted during writeback when all attributes can fit back into the base record.
- `ni_delete_all()` deallocates nonresident runs, removes NTFS3 object IDs/reparse records, frees attribute-list runs, frees subrecords, clears the base record in-use bit, writes records, and returns MFT records to the free set.
- `ni_new_attr_flags()` only allows sparse/compressed flag changes for empty nonresident files and ensures a file cannot be both sparse and compressed.
- `ni_parse_reparse()` recognizes symlink/mount-point style reparse points, WOF compressed files, and deduplicated files; WOF compression sets external compression bits for later frame reads.
- Native compressed reads/writes operate on compression frames. `ni_read_frame()` handles resident data, valid-size zeroing, native LZNT, and optional external LZX/XPRESS WOF data. `ni_write_frame()` compresses LZNT frames and updates allocated/sparse frame state.
- `ni_decompress_file()` converts WOF compressed files back to normal data by allocating clusters, reading/decompressing frames into the normal data stream, removing `WofCompressedData` and reparse attributes, and clearing sparse/reparse/compression cached state.
- Rename prefers add-new-name then remove-old-name to reduce failure risk, with undo support for the alternate strategy kept in code.
- `ni_write_inode()` updates standard info timestamps/flags, parent directory duplicate info, attribute lists, dirty subrecords, and the base MFT record. Empty dirty subrecords are freed.

## Dependencies

- MFT record helpers: `mi_get`, `mi_put`, `mi_write`, `mi_find_attr`, `mi_insert_attr`, `mi_remove_attr`, `mi_resize_attr`, `mi_pack_runs`.
- Attribute-list helpers: `al_find_ex`, `al_enumerate`, `al_add_le`, `al_remove_le`, `al_update`, `al_destroy`.
- Run/cluster helpers: `run_pack`, `run_unpack`, `run_deallocate`, `run_add_entry`, `ntfs_read_run`, `ntfs_write_run`.
- Directory index helpers: `indx_insert_entry`, `indx_delete_entry`, `indx_update_dup`.
- Compression helpers: LZNT always; LZX/XPRESS under `CONFIG_NTFS3_LZX_XPRESS`.
- VFS integration: page cache folios, inode timestamps, `ntfs_iget5()`, `mark_inode_dirty()`.

## Error and Safety Notes

- Attribute-list and subrecord operations are tightly coupled; many failures mark the inode bad or return `-EINVAL`.
- Several paths are intentionally best-effort, especially attribute-list repacking/removal and parent duplicate updates.
- Compression paths rely on full-frame locking and must carefully unlock/put every folio on failures.
- `ni_write_inode()` avoids blocking on busy inodes by re-dirtying and returning when `ni_trylock()` fails.
- Delayed allocation is resolved differently for sparse and normal files: sparse files allocate through `attr_data_get_block_locked()`, normal files through `attr_set_size_ex()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/frecord.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/fslog.c -->
# File Research: sources/os/linux/linux/fs/ntfs3/fslog.c

## Purpose

Implements NTFS `$LogFile` restart and replay for `ntfs3`. This is the mount-time journal recovery engine: it validates restart pages and log records, reconstructs restart tables, analyzes dirty pages and transactions, performs redo for dirty pages, performs undo for active transactions, updates MFT mirror state, and rewrites clean restart pages.

## Main Structures

- On-disk log/restart structures: `RESTART_HDR`, `RESTART_AREA`, `CLIENT_REC`, `LOG_REC_HDR`, `LFS_RECORD_HDR`, `RECORD_PAGE_HDR`.
- Restart tables: `RESTART_TABLE`, `OPEN_ATTR_ENRTY`, `DIR_PAGE_ENTRY`, `TRANSACTION_ENTRY`, `ATTR_NAME_ENTRY`.
- In-memory replay context: `struct ntfs_log`.
- Per-open-attribute runtime state: `struct OpenAttr`, holding copied attribute metadata and a run tree/reference.

## Main Interfaces

- Public entry point: `log_replay(struct ntfs_inode *ni, bool *initialized)`.
- Shared validator: `check_index_header()`.
- Restart/log helpers: `log_read_rst()`, `last_log_lsn()`, `read_rst_area()`, `read_log_rec_lcb()`, `read_next_log_rec()`.
- Replay mutator: `do_action()`, used by both redo and undo passes.
- Validation helpers: `check_rstbl()`, `check_log_rec()`, `check_file_record()`, `check_attr()`, `check_index_buffer()`, `check_index_root()`.

## Replay Flow

1. Normalize `$LogFile` page/file size and allocate page buffers.
2. Locate restart pages at the primary and secondary restart positions.
3. Select the newest valid restart area, or initialize a fresh log context if the log is uninitialized/CHKDSK-cleaned.
4. Validate supported log versions: 1.0, 1.1, and 2.0.
5. Ensure an `NTFS` client record exists in the restart area.
6. Read the client restart area and reconstruct restart tables:
   - transaction table,
   - dirty page table,
   - attribute name table,
   - open attribute table.
7. Convert legacy version-0 restart records to the current in-memory format where needed.
8. Analysis pass: walk records after the checkpoint, update transaction table state, update dirty page table LCN mappings, process open-attribute records, hotfixes, and transaction state records.
9. Compute the redo LSN from dirty pages and active transactions.
10. If replay is required and the mount is writable, reopen dirty attributes and rebuild/augment their run mappings.
11. Redo pass: walk forward from the redo LSN and apply redo operations for dirty pages whose oldest LSN requires them.
12. Undo pass: for active transactions, follow undo-next chains and apply undo operations.
13. Update MFT mirror, clear `NTFS_FLAGS_NEED_REPLAY`, and write clean restart pages unless read-only.

## `do_action()` Behavior

`do_action()` is the central redo/undo executor. Depending on the log operation, it may:

- Initialize, deallocate, or truncate MFT file record segments.
- Create/delete attributes in file records.
- Update resident values and mapping pairs.
- Set nonresident allocation/data/valid/total sizes.
- Add/delete/update index entries in root or allocation buffers.
- Set index VCNs.
- Update duplicate filename metadata.
- Update arbitrary record data.
- Set/clear bits in nonresident bitmaps.
- Write nonresident value buffers back through run mappings.

Before mutation it loads the target MFT record or target nonresident page, checks LSN ordering, validates file/index/attribute structure, and marks the volume dirty on suspicious corruption.

## Validation and Safety

- Restart-page validation checks signatures, page sizes, versions, restart offsets, USA/fixup layout, client list bounds, sequence-number bits, and restart-area bounds.
- Restart-table validation checks entry sizes, allocated/free-list offsets, free-list integrity, and total counts.
- Log-record validation checks operation target requirements, redo/undo alignment, LCN table consistency, and record length.
- MFT record validation checks file signatures, fixups, record size, used size, in-use status, and every attribute.
- Index validation checks root/allocation headers and entry chains before replaying index operations.
- LSN checks prevent replaying stale operations over newer on-disk records.
- If writable replay is needed but the mount is read-only, `log_replay()` leaves `NTFS_FLAGS_NEED_REPLAY` set and returns success for `-EROFS`.
- Unsupported log versions set dirty/error state and return `-EOPNOTSUPP`.

## Dependencies

- Low-level run I/O: `ntfs_read_run_nb_ra`, `ntfs_read_run_nb`, `ntfs_sb_write_run`.
- Fixup helpers: `ntfs_fix_post_read`, `ntfs_fix_pre_write`.
- MFT helpers: `mi_get`, `mi_write`, `mi_format_new`, `ni_load_mi_ex`, `ntfs_iget5`.
- Run helpers: `run_unpack`, `run_lookup_entry`, `run_add_entry`, `run_close`.
- Bitmap/index helpers: `ntfs_bitmap_set_le`, `ntfs_bitmap_clear_le`, `de_set_vbn_le`.
- Filesystem state: `ntfs_update_mftmirr`, `ntfs_set_state`, `NTFS_FLAGS_NEED_REPLAY`.

## Risk Notes

- This file is intentionally conservative: many malformed structures cause `log->set_dirty = true` rather than trying to continue silently.
- `last_log_lsn()` is complex because it handles wrapped logs, restart tail copies, partial I/O, multi-page records, and log version differences.
- Replay correctness depends on keeping the open attribute table synchronized with attribute mutations; `update_oa_attr()` refreshes copied attributes after relevant changes.
- The redo pass shortens or skips logged writes whose dirty-page LCNs were later deleted.
- The undo pass can expand in-memory attribute sizes so undo operations have addressable target space.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs3/fslog.c -->