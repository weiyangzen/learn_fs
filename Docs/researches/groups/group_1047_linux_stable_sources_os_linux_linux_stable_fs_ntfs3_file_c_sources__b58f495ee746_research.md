# Group Research: group_1047_linux_stable_sources_os_linux_linux_stable_fs_ntfs3_file_c_sources__b58f495ee746

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/file.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/file.c

## Summary
Implements the NTFS3 regular-file VFS surface: ioctls, getattr/setattr, mmap preparation, truncate/extend, fallocate, read/write/splice paths, compressed-file write handling, open/release, fiemap, fsync, llseek, and the exported inode/file operation tables.

## Main Responsibilities
- Provide regular-file `inode_operations` and `file_operations` for NTFS3.
- Dispatch NTFS3 ioctls for trim, filesystem label get/set, and forced shutdown.
- Enforce unsupported-feature restrictions for encrypted, deduplicated, compressed, immutable, and forced-shutdown files.
- Maintain NTFS file size and initialized-size semantics across truncate, extension, mmap write mappings, buffered I/O, direct I/O, and fallocate.
- Integrate with Linux iomap for buffered I/O, direct I/O, zeroing, fiemap, and page-cache backed writes.
- Handle native NTFS compressed write frames through `ni_read_frame()` and `ni_write_frame()`.
- Finalize delayed allocation and optional preallocation cleanup when the last writer closes a file.

## Key Interfaces
- `ntfs_ioctl()` and `ntfs_compat_ioctl()` implement `FITRIM`, `FS_IOC_GETFSLABEL`, `FS_IOC_SETFSLABEL`, and `NTFS3_IOC_SHUTDOWN`.
- `ntfs_getattr()` exposes NTFS birth time, cluster preferred block size, immutable/append/compressed/encrypted statx attributes.
- `ntfs_setattr()` handles size changes, chmod ACL updates, Windows readonly flag mirroring, and WSL permission persistence.
- `ntfs_fallocate()` implements punch-hole, collapse-range, insert-range, preallocation, sparse/compressed hole support, and keep-size handling.
- `ntfs_file_read_iter()`, `ntfs_file_write_iter()`, splice helpers, and mmap preparation form the main data I/O surface.
- `ntfs_file_fsync()` writes file data, inode metadata, parent directory duplicate info, MFT mirror updates, and block-device cache flushes.
- `ntfs_llseek()` supports `SEEK_DATA` and `SEEK_HOLE` through `ni_seek_data_or_hole()`.

## Important Behavior
Direct I/O is only attempted when `ntfs_dio_alignment()` returns a real block alignment and both file offset and iterator alignment satisfy it. Resident files without delayed allocation bypass DIO; files with delayed allocation force allocation before direct reads/writes because DIO cannot safely operate on delalloc runs.

Writes call `generic_write_checks()`, `file_modified()`, `ntfs_extend()`, and then either compressed-frame writing, buffered iomap writing, direct iomap writing, or a mixed DIO-to-buffered fallback. The fallback writes and invalidates page-cache pages to preserve direct-I/O semantics for the remainder of a partially completed request.

Initialized size is explicit NTFS state (`ni->i_valid`). `ntfs_extend_initialized_size()` zeroes the gap through iomap for nonresident files, while resident files can simply move `i_valid`. mmap write preparation allocates sparse clusters and extends initialized size up to the mapped writable range, installing custom VM ops so `close` can mark `i_valid` advanced after writable mappings.

Fallocate coordinates page-cache writeback/invalidation, DIO quiescing, inode locking, and NTFS attribute helpers. Punching an unaligned compressed/sparse frame zeroes head/tail pieces and deallocates only the aligned interior. Insert and collapse range are protected by invalidate locks and write out affected cache ranges before metadata movement.

Compressed writes operate one NTFS LZNT frame at a time. The code locks or creates all pages in a frame, reads existing frame data when partial updates require it, copies user data atomically, calls `ni_write_frame()` under `ni_lock()`, clears dirty state, unlocks pages, and updates file position, initialized size, and inode size.

## State and Synchronization
The file uses VFS inode locks, shared inode locks for DIO reads/fiemap/seek, `inode_dio_wait()` before range mutation, `filemap_invalidate_lock()` around hole/range operations, `ni_lock()`, and `ni->file.run_lock` for runlist/attribute size changes. It marks NTFS volume state dirty before mutating metadata and marks inodes dirty after size/time/attribute updates.

## Cross-File Interactions
Most metadata work is delegated to `attrib.c` helpers such as `attr_set_size_ex()`, `attr_data_get_block()`, `attr_punch_hole()`, `attr_collapse_range()`, `attr_insert_range()`, and `attr_force_nonresident()`. I/O mapping is delegated to `ntfs_iomap_ops` and `ntfs_iomap_folio_ops`. Compressed read/write frame mechanics and delayed allocation finalization come from `frecord.c` through `ni_read_frame()`, `ni_write_frame()`, and `ni_allocate_da_blocks()`.

## Risks
Correctness depends on preserving NTFS initialized-size semantics so reads beyond `i_valid` return zeroes and writes cannot expose stale disk data. Range fallocate paths are sensitive to page-cache invalidation and DIO ordering. Compressed files have many unsupported combinations, especially DIO, writable mmap, external compression without `CONFIG_NTFS3_LZX_XPRESS`, and deduplicated/encrypted data. Last-writer release can still fail while allocating delayed blocks or trimming preallocation, so callers must handle release-time errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/frecord.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/frecord.c

## Summary
Implements NTFS3 MFT-record and file-record management for `struct ntfs_inode`. It owns MFT subrecord loading/caching, attribute discovery and insertion/removal, attribute-list creation/expansion/compaction, whole-inode deletion, filename attribute maintenance, sparse/compressed flag transitions, reparse interpretation, compressed frame I/O, directory name updates, inode dirtiness/writeback, parent duplicate-info propagation, and delayed-allocation materialization.

## Main Responsibilities
- Maintain the per-inode red-black tree of loaded extension MFT records.
- Locate, enumerate, insert, remove, and move attributes across primary and extension records.
- Create, update, expand, shrink, and remove NTFS `$ATTRIBUTE_LIST` data.
- Allocate and free child MFT records for attributes that do not fit in the base record.
- Delete all attributes and deallocate all nonresident runs when an unlinked inode is cleared.
- Implement native LZNT compressed frame reads/writes and optional WOF LZX/XPRESS external decompression.
- Maintain `$FILE_NAME` attributes and parent directory indexes during link removal, add, undo, and rename.
- Write dirty base and extension MFT records, update standard information, update parent duplicate records, and free empty extension records.
- Allocate delayed-allocation clusters before direct I/O, close, or other paths that require real mappings.

## Key Interfaces
- MFT subrecord helpers: `ni_load_mi_ex()`, `ni_load_mi()`, `ni_load_all_mi()`, `ni_add_subrecord()`, `ni_remove_mi()`.
- Attribute lookup/enumeration: `ni_find_attr()`, `ni_enum_attr_ex()`, `ni_std()`, `ni_std5()`.
- Attribute mutation: `ni_insert_resident()`, `ni_insert_nonresident()`, `ni_remove_attr()`, `ni_remove_attr_le()`, `ni_create_attr_list()`, `ni_expand_list()`.
- Cleanup and deletion: `ni_clear()`, `ni_delete_all()`.
- Compression/reparse: `ni_parse_reparse()`, `ni_read_folio_cmpr()`, `ni_read_frame()`, `ni_write_frame()`, and `ni_decompress_file()` when LZX/XPRESS support is compiled in.
- Name operations: `ni_fname_name()`, `ni_fname_type()`, `ni_remove_name()`, `ni_remove_name_undo()`, `ni_add_name()`, `ni_rename()`.
- Writeback and allocation: `ni_is_dirty()`, `ni_write_parents()`, `ni_write_inode()`, `ni_allocate_da_blocks()`, `ni_allocate_da_blocks_locked()`.

## Important Behavior
`ni_find_attr()` switches between simple base-record lookup and attribute-list lookup. When an attribute list is present, it finds the list entry, loads the referenced MFT record, finds the concrete attribute by id, and validates VCN coverage. Inconsistency marks the VFS inode bad.

Attribute insertion first tries the primary MFT record, then extension records, then allocates a new child record. `$STANDARD_INFORMATION`, `$ATTRIBUTE_LIST`, and `$LogFile` attributes cannot be externalized. `$MFT::$DATA` is special: its first segment must remain in the base MFT record, so insertion can evict other attributes or split the MFT data attribute through `ni_expand_mft_list()`.

`ni_create_attr_list()` builds an attribute list from base-record attributes and moves enough movable attributes to a child record to fit the resident list. `ni_try_remove_attr_list()` performs the reverse optimization when all attributes can fit back into the primary record, copying a backup of the MFT record so it can restore the primary record on failure.

`ni_delete_all()` enumerates all attributes, removes NTFS3 reparse/object-id side records when relevant, deallocates every nonresident run by unpacking mapping pairs with `RUN_DEALLOCATE`, deallocates the attribute-list run, frees child MFT records, marks the base record free, and updates the MFT bitmap.

`ni_new_attr_flags()` handles sparse/compressed flag changes only for empty data attributes. It prevents simultaneous sparse and compressed flags, resizes the nonresident attribute header between normal and extended forms, updates compression unit state, and switches the inode mapping aops between normal and compressed address-space operations.

`ni_parse_reparse()` recognizes symlink/mount-point style name-surrogate reparses, WOF external compression reparses, and dedup reparses. WOF parsing records the external compression frame size in inode flags; dedup marks the inode as deduplicated so higher-level I/O paths reject unsupported access.

Compressed-frame I/O maps a whole compression frame with `vmap()`. Native LZNT reads detect resident data, sparse frames, uncompressed frames, and compressed frames; writes compress the page array, choose sparse/compressed/uncompressed frame layout, update allocation through `attr_allocate_frame()`, and write packed data to the runlist. Optional WOF decompression reads `WofCompressedData`, uses shared LZX/XPRESS decompressor contexts, writes decompressed data to normal data runs, removes WOF/reparse attributes, and clears cached compression state.

Name operations deliberately add the new name before removing the old name during rename. This avoids the harder failure mode where the old name is removed but the new one cannot be allocated and restoration fails. Removal tracks undo state for paired DOS/Win32 names.

`ni_write_inode()` updates timestamps and file attributes in `$STANDARD_INFORMATION`, updates parent directory duplicate information unless the inode is metadata or inactive, writes dirty attribute lists, writes dirty child records, frees empty child records, and finally writes the base record. If parent indexes cannot be locked, it leaves `NI_FLAG_UPDATE_PARENT` set and redirties the inode for a later pass.

## State and Synchronization
The file uses `ni_lock()` around inode metadata mutation, `ni->file.run_lock` around runlist and data-size mutations, page and folio locks for compressed I/O, and the inode dirty flag protocol for MFT writeback. Child MFT records live in `ni->mi_tree`; attribute-list state is in `ni->attr_list`; file data run state is in `ni->file.run` and delayed allocation in `ni->file.run_da`.

## Cross-File Interactions
This file is the metadata backend used by `file.c`, `inode.c`, `namei.c`, `index.c`, `attrib.c`, and mount/writeback code. It depends on `mi_*` record primitives, `al_*` attribute-list helpers, `run_*` mapping-pair helpers, `attr_*` allocation/size/frame helpers, `indx_*` directory index helpers, object-id and reparse indexes, LZNT/LZX/XPRESS library code, and VFS inode lookup/writeback.

## Risks
Attribute-list and extension-record code is pointer-sensitive: adding a list entry can resize/move list storage, and moving attributes invalidates pointers into MFT records. The `$MFT::$DATA` bootstrap rules are fragile because extension record placement must not conflict with MFT data coverage. Compression paths must keep frame size, page count, runlist locking, and valid-size zeroing consistent. Parent duplicate-info updates are best-effort and can defer through dirty flags, so writeback ordering matters. `ni_clear()` can delete all metadata for an unlinked inode unless log replay is active, making link count and replay flags critical.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/frecord.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/fslog.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs3/fslog.c

## Summary
Implements NTFS `$LogFile` restart parsing and crash replay for NTFS3. It defines the on-disk restart/log record structures, validates restart pages and log pages, reconstructs the active log tail, reads client restart data and restart tables, performs analysis/redo/undo passes, applies logged metadata operations to MFT records and index/allocation buffers, rewrites clean restart pages, and tracks when the volume must remain dirty or needs replay.

## Main Responsibilities
- Define NTFS log structures: restart headers/areas, client records, restart tables, open attribute entries, dirty page entries, transaction entries, NTFS restart records, LFS record headers, and record page headers.
- Validate restart page headers, restart areas, client lists, restart tables, log records, MFT records, attributes, index roots, and index buffers before replay mutation.
- Convert between LSNs, file offsets, sequence numbers, and circular-log page offsets.
- Read restart pages and log record pages with USA fixup handling and support for multi-page log records.
- Determine the last valid LSN, including tail-copy and partial-I/O recovery logic.
- Rebuild in-memory open-attribute, dirty-page, attribute-name, and transaction tables from the client restart area and subsequent log records.
- Reopen attributes and reconstruct run mappings needed to replay dirty pages.
- Apply redo operations for dirty pages and undo operations for active uncommitted transactions.
- Mark the volume dirty on replay inconsistency and preserve `NTFS_FLAGS_NEED_REPLAY` when replay cannot complete.

## Key Interfaces
- `log_replay()` is the exported mount-time entry point.
- `check_index_header()` is exported for index validation outside the local replay helpers.
- Local log reading helpers include `read_log_page()`, `log_read_rst()`, `last_log_lsn()`, `read_log_rec_buf()`, `read_rst_area()`, `find_log_rec()`, `read_log_rec_lcb()`, and `read_next_log_rec()`.
- Restart-table helpers include `check_rstbl()`, `enum_rstbl()`, `init_rsttbl()`, `extend_rsttbl()`, `alloc_rsttbl_idx()`, `alloc_rsttbl_from_idx()`, and `free_rsttbl_idx()`.
- `do_action()` is the common redo/undo operation applicator.

## Important Behavior
Replay starts by normalizing the `$LogFile` page size and reading one or two restart pages. If no restart area exists and the log is uninitialized, the code creates an in-memory clean restart area. If a valid restart area exists, it imports page/log sizing, current LSN, sequence-number layout, client records, and open-log count, then calls `last_log_lsn()` to reconcile tail copies and the actual final written log record.

Only NTFS log versions 1.0, 1.1, and 2.0 are accepted. Unsupported versions set the dirty flag and return `-EOPNOTSUPP`. The code also handles legacy restart table formats by converting 32-bit open-attribute and dirty-page entries to the in-memory version-1 form.

The analysis pass begins at the checkpoint LSN, reads forward to the end of the log, updates or creates transaction table entries, updates the dirty page table for records with LCNs, handles `DeleteDirtyClusters` and `HotFix`, tracks open nonresident attributes, and computes the earliest redo LSN from dirty pages and active transactions.

Before redo, the code reopens every logged open attribute. It tries to load the referenced inode and attribute; if it cannot, it creates a synthetic nonresident attribute with an empty runlist so replay can still reason about log records. It then merges dirty-page LCNs into the corresponding run mappings, except for protected early metadata ranges.

The redo pass walks forward from the redo LSN. For each log record that targets a dirty page and is not older than that page's oldest LSN, it verifies the target attribute mapping, trims redo length for deleted clusters, skips no-op/control operations, and calls `do_action()` with the record LSN so MFT/index record LSNs are updated.

The undo pass scans active transactions. It follows each transaction's undo-next chain and applies the logged undo operation through `do_action()` without an LSN pointer, then frees the transaction table entry. Prepared/committed/nonactive transactions are skipped or freed as appropriate.

`do_action()` supports MFT-record operations, resident value changes, nonresident value writes, mapping-pair changes, attribute size updates, root and allocation index entry changes, filename duplicate updates, nonresident bitmap bit set/clear, and record data updates. It validates offsets before every memmove/memcpy, uses `check_lsn()` to avoid replaying stale operations, writes dirty MFT records with `mi_write()`, and writes dirty nonresident buffers back through the reconstructed run mapping.

At successful replay completion, the code updates the MFT mirror, clears `NTFS_FLAGS_NEED_REPLAY`, and writes two clean restart pages with no active client. On read-only mounts, it can analyze enough to leave replay needed without mutating the device; `-EROFS` is converted to success on exit while the replay-needed state remains visible.

## State and Synchronization
`struct ntfs_log` is the central replay context. It holds page sizing, circular-log offsets, LSN sequence fields, restart-area copy, active client id, restart tables, current/oldest/last LSN state, log flags, read-ahead state, and whether replay detected dirty-volume conditions. Replay uses inode lookup/reference ownership, `mi_get()`/`mi_write()` for records not already cached, runlist reconstruction for open attributes, and `ntfs_fix_post_read()`/`ntfs_fix_pre_write()` around multi-sector protected records.

## Cross-File Interactions
Replay uses NTFS3 record schemas from `ntfs.h`/`ntfs_fs.h`, MFT record helpers from `record.c`/`mft.c`, inode loading via `ntfs_iget5()`, attribute lookup and subrecord loading via `frecord.c`, runlist and mapping-pair helpers, bitmap bit helpers, index validation/layout helpers, block-run read/write helpers, and MFT mirror update logic.

## Risks
This file is security- and corruption-sensitive because it replays untrusted on-disk log data into live metadata. Bounds checks on restart tables, attributes, index entries, MFT record `used` sizes, log record offsets, and dirty-page LCN arrays are critical; many later memmove lengths rely on earlier validation. Circular-log tail reconstruction is complex and must distinguish valid tail copies, partial I/O, USA failures, wrapping, and stale pages. Synthetic open attributes allow replay to continue when referenced metadata is damaged, but also make correct dirty-volume marking important. Any replay failure leaves `NTFS_FLAGS_NEED_REPLAY` set and may mark the volume dirty/error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs3/fslog.c -->