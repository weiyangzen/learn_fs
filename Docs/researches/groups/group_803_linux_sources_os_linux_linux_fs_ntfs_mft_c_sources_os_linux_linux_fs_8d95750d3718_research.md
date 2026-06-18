# Group Research: group_803_linux_sources_os_linux_linux_fs_ntfs_mft_c_sources_os_linux_linux_fs_8d95750d3718

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/mft.c -->
# File Research: sources/os/linux/linux/fs/ntfs/mft.c

Core NTFS MFT record management: validates, maps, writes, allocates, frees, mirrors, and writebacks MFT records.

Key responsibilities:
- Validates MFT record structure in `ntfs_mft_record_check()`: `FILE` magic, USA/fixup fields, allocation size, in-use size, and attribute offset bounds.
- Maps records through `$MFT` page cache with `map_mft_record()` and `map_mft_record_folio()`, copying record bytes into `ni->mrec`, applying `post_read_mst_fixup()`, and retaining the source folio and offset.
- Handles extent records via `map_extent_mft_record()`, including base inode reference management, extent cache lookup, sequence validation, and dynamic `extent_ntfs_inos` growth.
- Marks MFT metadata dirty through `__mark_mft_record_dirty()` and base VFS inode `I_DIRTY_DATASYNC`.
- Writes records with MST protection in `write_mft_record_nolock()` and updates `$MFTMirr` for mirrored records via `ntfs_sync_mft_mirror()`.
- Controls page-cache writeback of `$MFT` folios in `ntfs_mft_writepages()` and `ntfs_write_mft_block()`.

Allocation and growth:
- `ntfs_mft_bitmap_find_and_alloc_free_rec_nolock()` scans `$MFT/$BITMAP`, skipping records below `RESERVED_MFT_RECORDS` except special `$MFT` extension behavior.
- `ntfs_mft_bitmap_extend_allocation_nolock()` grows bitmap allocation by appending or allocating a cluster, then rebuilds mapping pairs and rolls back on failure.
- `ntfs_mft_bitmap_extend_initialized_nolock()` extends initialized bitmap bytes by 8 and zeros them.
- `ntfs_mft_data_extend_allocation_nolock()` extends `$MFT/$DATA`, updates runlists and mapping pairs, and rolls back allocated clusters if metadata updates fail.
- `ntfs_mft_record_layout()` formats an empty record with valid USA, attributes offset, `AT_END`, sequence number, and NTFS 3.1 record number when applicable.
- `ntfs_mft_record_alloc()` orchestrates bitmap allocation, `$MFT` growth, record formatting, inode setup, extent attachment, dirtying, rollback, and free-record accounting.
- `ntfs_mft_record_free()` clears `MFT_RECORD_IN_USE`, bumps sequence number, writes the record, clears the bitmap bit, and rolls back where possible.

Concurrency and writeback:
- Uses `mrec_lock`, `extent_lock`, `mftbmp_lock`, runlist locks, and `lcnbmp_lock`; several paths explicitly preserve lock ordering.
- `ntfs_may_write_mft_record()` avoids deadlocks during folio writeback by checking inode cache state, dirty state, deletion/creation state, and trying mrec locks without blocking.
- Deferred `iput()` handling avoids dropping inode refs while holding folio locks.
- Async BIO writes retain folios through `ntfs_bio_end_io()` to prevent eviction while I/O is in flight.

Failure behavior:
- Sets `NVolErrors()` when rollback or write failures can leave metadata inconsistent.
- Converts stale extent/base sequence references to `-EIO`.
- Leaves dirty records dirty or redirties on retryable write failures.
- Enforces the 2^32 MFT-record limit.

Important dependencies:
- MST helpers from `mst.c`.
- Bitmap operations from `bitmap.h`.
- Cluster allocation/free from `lcnalloc.h`.
- Attribute lookup, resizing, mapping pairs, and runlist manipulation.
- Folio, BIO, iomap, and writeback kernel APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/mft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/mft.h -->
# File Research: sources/os/linux/linux/fs/ntfs/mft.h

Public MFT API header for NTFS.

Exports:
- Record mapping: `map_mft_record()`, `unmap_mft_record()`, `map_extent_mft_record()`, `unmap_extent_mft_record()`.
- Dirtying: `__mark_mft_record_dirty()` and inline `mark_mft_record_dirty()`, which only calls the heavy path when the inode was not already marked dirty.
- Write helpers: `ntfs_sync_mft_mirror()`, `write_mft_record_nolock()`, inline `write_mft_record()`.
- Allocation/free/check/writeback: `ntfs_mft_record_alloc()`, `ntfs_mft_record_free()`, `ntfs_mft_record_check()`, `ntfs_mft_writepages()`, `ntfs_mft_mark_dirty()`.
- Declares `ntfs_mft_records_write()`, though that implementation is not in the grouped `mft.c`.

Notable behavior:
- Inline `write_mft_record()` locks the containing folio around `write_mft_record_nolock()` to serialize inode writeback and page-cache writeback paths.
- Header depends on `inode.h`, highmem, and pagemap types.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/mft.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/mst.c -->
# File Research: sources/os/linux/linux/fs/ntfs/mst.c

Implements NTFS Multi Sector Transfer protection fixups.

Key functions:
- `post_read_mst_fixup()` validates the update sequence array, detects incomplete multi-sector transfers, marks bad records as `BAAD`, and restores original sector-end words.
- `pre_write_mst_fixup()` increments the update sequence number, stores original sector-end words into the USA, and writes the sequence value into each protected sector tail before disk write.
- `post_write_mst_fixup()` restores protected words after a pre-write fixup without validation.

Semantics:
- `post_read_mst_fixup()` treats absent/invalid USA as “not protected” and returns success.
- `pre_write_mst_fixup()` treats absent/invalid USA as an error because callers must prepare a valid record header.
- Update sequence numbers skip `0` and `0xffff`.

Important dependencies:
- NTFS layout constants and record magic helpers from `ntfs.h`.
- Ratelimited logging for incomplete transfer diagnostics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/mst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/namei.c -->
# File Research: sources/os/linux/linux/fs/ntfs/namei.c

Implements NTFS directory inode operations, namespace lookup, create/delete/link/rename, symlink/mknod support, and NFS export helpers.

Lookup:
- `ntfs_lookup()` converts dentries to Unicode and calls `ntfs_lookup_inode_by_name()`.
- Handles exact WIN32/POSIX matches directly through `d_splice_alias()`.
- Handles case-insensitive WIN32 matches with `d_add_ci()`.
- Handles DOS short-name matches by loading the inode, locating the corresponding WIN32 `FILE_NAME` attribute, converting it to NLS, then returning the canonical dentry.
- Checks MFT reference sequence numbers to reject stale directory index entries.

Name validation:
- `ntfs_check_bad_char()` rejects NTFS/Windows-disallowed characters and control chars.
- `ntfs_check_bad_windows_name()` optionally rejects trailing space/dot and reserved DOS device names like `AUX`, `CON`, `NUL`, `PRN`, `COM1`-`COM9`, and `LPT1`-`LPT9`.

Create path:
- `__ntfs_create()` creates a VFS inode, initializes NTFS inode state, allocates an MFT record, sets `I_NEW | I_CREATING`, inserts into inode hash, and constructs core attributes.
- Adds `STANDARD_INFORMATION`, a permissive `SECURITY_DESCRIPTOR`, directory `INDEX_ROOT` or unnamed `DATA`, WSL EA metadata, and a POSIX `FILE_NAME`.
- For symlinks and special files, creates WSL-compatible reparse data via `ntfs_reparse_set_wsl_symlink()` or `ntfs_reparse_set_wsl_not_symlink()`.
- Adds the filename to the parent directory index and updates link count.
- Rollback removes created attributes, reparse index entries, extent records, and MFT record on failure.

Delete/unlink/rmdir:
- `ntfs_delete()` removes matching `FILE_NAME` attributes and directory index entries.
- Handles DOS/WIN32 paired names, case-sensitive first then case-insensitive fallback.
- Checks directory emptiness, with hard-link-aware handling for directories.
- When link count reaches zero, sets `NInoBeingDeleted()`, deletes reparse and object-id index entries, and clears attribute inode links.

Hard links and rename:
- `__ntfs_link()` adds a new POSIX `FILE_NAME` attribute and parent index entry, then increments MFT/VFS link counts.
- `ntfs_rename()` rejects exchange/whiteout, optionally deletes existing target, links old inode into the new directory, deletes the old name, and attempts rollback if old-name deletion fails.

VFS operations:
- `ntfs_dir_inode_ops` wires lookup, create, unlink, mkdir, rmdir, rename, ACL, xattr, setattr/getattr, symlink, mknod, and link.
- `ntfs_create()`, `ntfs_mkdir()`, `ntfs_symlink()`, and `ntfs_mknod()` all mark the volume dirty before metadata mutation.

Export support:
- `ntfs_get_parent()` reads the first valid resident `FILE_NAME` attribute to obtain parent MFT reference.
- `ntfs_export_ops` uses generic file-handle encoding/decoding with sequence generation checks.

Important dependencies:
- Attribute, index, EA, reparse, object-id, ACL, timestamp, MFT, and Unicode conversion helpers.
- Careful nested locking of child, old/new parent, and target mrec locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/ntfs.h -->
# File Research: sources/os/linux/linux/fs/ntfs/ntfs.h

Top-level NTFS driver header.

Defines:
- Common includes and `pr_fmt`.
- Defaults and constants: `NTFS_DEF_PREALLOC_SIZE`, `STANDARD_COMPRESSION_UNIT`, `MAX_COMPRESSION_CLUSTER_SIZE`, `NTFS_BLOCK_SIZE`, `NTFS_SB_MAGIC`, max name/label lengths.
- Case comparison constants: `CASE_SENSITIVE`, `IGNORE_CASE`.
- Byte/cluster/MFT/folio/sector conversion macros and inline equivalents.

Exports:
- Slab caches for names, inodes, big inodes, attribute contexts, and index contexts.
- Address-space, file, inode, directory, empty-file, and export operation tables.
- `NTFS_SB()` accessor.
- Compression, superblock, MST, Unicode, ioctl, upcase, and block-device I/O function declarations.

Utility:
- `ntfs_ffs()` implements a local find-first-set helper.

Role:
- This header is the shared dependency surface for the NTFS driver files in this group, especially `mft.c`, `mst.c`, `namei.c`, `reparse.c`, and `runlist.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/ntfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/object_id.c -->
# File Research: sources/os/linux/linux/fs/ntfs/object_id.c

Maintains `$Extend/$ObjId` index cleanup for NTFS object IDs.

Data structures:
- `object_id_index_key`: GUID key.
- `object_id_index_data`: file reference and birth/domain GUIDs.
- `object_id_index`: index entry layout for `$ObjId`.
- Global index name `objid_index_name` is `$O`.

Key flow:
- `open_object_id_index()` opens `FILE_Extend`, looks up `$ObjId`, opens its inode, and obtains the `$O` index context.
- `remove_object_id_index()` reads the existing `AT_OBJECT_ID` attribute GUID from the inode attribute stream and removes the matching index entry when found.
- `ntfs_delete_object_id_index()` opens the object-id attribute inode, opens the global object-id index, locks the index inode mrec, removes the entry, marks the index entry and MFT record dirty, and drops references.

Failure behavior:
- Missing object-id data returns `-ENODATA`.
- If `$ObjId` or its index cannot be opened, deletion silently does no index update and returns current `ret`.
- Uses `PTR_ERR()` from `ntfs_attr_iget()` when object-id attribute lookup fails.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/object_id.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/object_id.h -->
# File Research: sources/os/linux/linux/fs/ntfs/object_id.h

Header for object-id index support.

Exports:
- `objid_index_name`.
- `ntfs_delete_object_id_index()`.

Role:
- Used by deletion paths to remove stale `$Extend/$ObjId` index entries when an inode with `AT_OBJECT_ID` loses its last link.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/object_id.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/quota.c -->
# File Research: sources/os/linux/linux/fs/ntfs/quota.c

Handles marking NTFS quota metadata out of date.

Key function:
- `ntfs_mark_quotas_out_of_date()` opens the quota `$Q` index on `vol->quota_q_ino`, finds the defaults entry `QUOTA_DEFAULTS_ID`, validates entry size and `QUOTA_VERSION`, and sets `QUOTA_FLAG_OUT_OF_DATE` when quota tracking/request/pending-delete state requires it.

Behavior:
- Skips work if the volume already has `NVolQuotaOutOfDate()`.
- Requires `vol->quota_ino` and `vol->quota_q_ino`.
- Marks the index entry dirty after changing flags.
- Sets the in-memory volume flag so remount paths do not repeat the operation.

Failure behavior:
- Returns `false` on missing quota inodes, lookup failure, invalid entry size, or unsupported quota version.
- Always releases index context and unlocks `quota_q_ino` on error paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/quota.h -->
# File Research: sources/os/linux/linux/fs/ntfs/quota.h

Header for NTFS quota handling.

Exports:
- `ntfs_mark_quotas_out_of_date(struct ntfs_volume *vol)`.

Role:
- Provides the quota out-of-date marker used by mount/remount or metadata-changing paths that need Windows to rescan quota state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/reparse.c -->
# File Research: sources/os/linux/linux/fs/ntfs/reparse.c

Handles NTFS reparse point validation, interpretation, creation, indexing, and deletion, with explicit support for WSL-style symlinks and special files.

Validation and interpretation:
- `ntfs_is_valid_reparse_buffer()` validates header size, nonzero tag, Microsoft vs non-Microsoft header sizing, and exact expected size.
- `valid_reparse_data()` adds tag-specific checks for WSL symlinks, AF_UNIX sockets, FIFO, char, and block devices.
- `ntfs_reparse_tag_mode()` maps reparse tags to Linux mode type bits.
- `ntfs_make_symlink()` reads `AT_REPARSE_POINT`, validates it, extracts WSL symlink target into `ni->target`, and returns the implied mode.
- `ntfs_reparse_tag_dt_types()` opens an inode by MFT reference, reads reparse data, and maps tags to directory-entry types.

Index handling:
- Global `reparse_index_name` is `$R`.
- `open_reparse_index()` opens `FILE_Extend`, looks up `$Reparse`, opens its inode, and gets the `$R` index context.
- `set_reparse_index()` builds and inserts a `$Reparse` index entry keyed by tag and file reference.
- `remove_reparse_index()` reads the old tag from the reparse attribute and removes the matching index entry.

Mutation:
- `update_reparse_data()` opens the `AT_REPARSE_POINT` attribute inode, removes any old index entry, overwrites reparse data, inserts the new index entry, and marks metadata dirty.
- `ntfs_delete_reparse_index()` removes the index entry and clears `FILE_ATTR_REPARSE_POINT` from inode flags/name metadata.
- `ntfs_set_ntfs_reparse_data()` creates the reparse attribute if needed, validates NTFS version, sets inode flags, updates data and index, and rolls back flags on failure.
- `ntfs_reparse_set_wsl_symlink()` converts target to NLS bytes, builds `IO_REPARSE_TAG_LX_SYMLINK` data, stores it, and keeps `ni->target` on success.
- `ntfs_reparse_set_wsl_not_symlink()` creates zero-length WSL special-file reparse data for socket/FIFO/char/block device tags.

Notable observation:
- `reparse.h` declares `ntfs_remove_ntfs_reparse_data()`, but this grouped `reparse.c` does not define it.

Important dependencies:
- Attribute read/write/add/remove APIs, index APIs, MFT dirtying, Unicode conversion, and NTFS layout tag definitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/reparse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/reparse.h -->
# File Research: sources/os/linux/linux/fs/ntfs/reparse.h

Header for reparse point support.

Exports:
- `reparse_index_name`.
- `ntfs_make_symlink()`.
- `ntfs_reparse_tag_dt_types()`.
- `ntfs_reparse_set_wsl_symlink()`.
- `ntfs_reparse_set_wsl_not_symlink()`.
- `ntfs_delete_reparse_index()`.
- `ntfs_remove_ntfs_reparse_data()` declaration.

Notable:
- `ntfs_remove_ntfs_reparse_data()` is declared here but not implemented in the grouped `reparse.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/reparse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/runlist.c -->
# File Research: sources/os/linux/linux/fs/ntfs/runlist.c

Implements NTFS runlist allocation, merging, mapping-pairs compression/decompression, truncation, sparse/compressed-size checks, and range transforms.

Memory and primitive helpers:
- `ntfs_rl_realloc()` reallocates runlist arrays with `kvzalloc()` and preserves existing entries.
- `ntfs_rl_realloc_nofail()` provides no-fail growth for marker repair paths.
- `ntfs_rl_mm()` and `ntfs_rl_mc()` wrap runlist `memmove()`/`memcpy()`.
- `ntfs_are_rl_mergeable()` and `__ntfs_rl_merge()` detect/perform adjacent run merging for physical runs, holes, delayed allocation, and unmapped regions.

Runlist merge:
- `ntfs_runlists_merge()` merges a decompressed or newly allocated source runlist into an existing destination runlist.
- Supports insertion at hole start, split hole insertion, append at hole end, whole-hole replacement, and appending at end.
- Preserves/creates `LCN_RL_NOT_MAPPED` and `LCN_ENOENT` markers for partially mapped attributes and future extents.
- Frees the source runlist on successful merge.

Mapping-pairs decode:
- `ntfs_mapping_pairs_decompress()` parses NTFS mapping pairs into runlist elements.
- Validates `lowest_vcn`, mapping-pairs offset, length entries, VCN overflow, invalid negative LCNs, invalid zero-sized non-hole runs, and `highest_vcn`.
- Represents sparse runs as `LCN_HOLE`.
- Adds unmapped regions when more extents follow.
- Merges into an old runlist if provided.

Mapping-pairs encode:
- `ntfs_get_size_for_mapping_pairs()` computes required encoded size for a runlist range, including sparse-run rules for NTFS 3+.
- `ntfs_write_significant_bytes()` writes minimal signed little-endian byte sequences.
- `ntfs_mapping_pairs_build()` encodes runlists into mapping pairs, supports partial success with `stop_vcn`/`stop_rl`, counts delayed-allocation clusters, and rejects unmapped/corrupt runs.

Lookup and truncation:
- `ntfs_rl_vcn_to_lcn()` maps VCN to LCN or special negative status.
- `ntfs_rl_find_vcn_nolock()` returns the element containing a VCN if mapped or valid terminator.
- `ntfs_rl_truncate_nolock()` shrinks, expands with holes, or preserves terminator state for a locked runlist.

Sparse/compressed helpers:
- `ntfs_rl_sparse()` reports whether the runlist contains holes or delayed allocation.
- `ntfs_rl_get_compressed_size()` sums physically allocated run lengths and converts to bytes.

Range transforms:
- `ntfs_rl_insert_range()` inserts a source range into a destination runlist, splitting and merging contiguous runs.
- `ntfs_rl_punch_hole()` extracts a physical range into `punch_rl`, replaces it with a hole, handles split endpoints, and merges neighboring holes.
- `ntfs_rl_collapse_range()` extracts and removes a range, shifts following VCNs down, and merges adjacent compatible runs.

Important invariants:
- Runlists are VCN-ordered and terminated with a zero-length element, usually `LCN_ENOENT`.
- Special negative LCN values carry semantic states: hole, delayed allocation, not mapped, not found, memory/I/O/invalid errors.
- Callers must hold runlist locks where noted; most functions do not lock internally.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/runlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/runlist.h -->
# File Research: sources/os/linux/linux/fs/ntfs/runlist.h

Public header for NTFS runlist handling.

Defines:
- `struct runlist_element` with `vcn`, `lcn`, and `length`.
- `struct runlist` with runlist pointer, read/write semaphore, element count, and hint index.
- `ntfs_init_runlist()` initializer.
- Special negative LCN/status constants: `LCN_DELALLOC`, `LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`, `LCN_ENOMEM`, `LCN_EIO`, `LCN_EINVAL`.

Exports:
- Merge/decompress/lookup helpers: `ntfs_runlists_merge()`, `ntfs_mapping_pairs_decompress()`, `ntfs_rl_vcn_to_lcn()`, `ntfs_rl_find_vcn_nolock()`.
- Mapping-pairs encode sizing/build APIs.
- Truncate, sparse, compressed-size, insert, punch-hole, collapse-range, and realloc APIs.

Role:
- Shared runlist abstraction used by attribute mapping, MFT growth, cluster allocation, writeback, and sparse/compressed data handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/runlist.h -->