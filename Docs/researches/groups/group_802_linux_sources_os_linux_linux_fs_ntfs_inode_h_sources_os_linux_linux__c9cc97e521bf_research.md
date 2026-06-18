# Group Research: group_802_linux_sources_os_linux_linux_fs_ntfs_inode_h_sources_os_linux_linux__c9cc97e521bf

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`, so all listed NTFS Linux driver files are in scope. Each source file below was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/inode.h -->
# File Research: sources/os/linux/linux/fs/ntfs/inode.h

This header defines the NTFS driver's in-memory inode model and its primary inode-facing APIs. It extends the VFS inode through `struct big_ntfs_inode`, where `struct ntfs_inode` is embedded before `struct inode`, and provides `NTFS_I()` / `VFS_I()` container conversion helpers.

Key data model:
- `struct ntfs_inode` stores NTFS-specific state: MFT number/sequence, volume pointer, attribute identity, runlist, size triplet (`data_size`, `initialized_size`, `allocated_size`), MFT record cache fields, attribute-list state, index/compression subtype metadata, extent tracking, delayed allocation cluster count, and symlink target.
- `enum ntfs_inode_mutex_lock_class` provides lockdep classes for parent/child/extent/EA locking patterns.
- The `state` bitset is exposed via generated `NIno*`, `NInoSet*`, `NInoClear*`, and selected test-and-set/test-and-clear helpers. State flags cover dirty MFT records, attribute lists, fake attribute inodes, MST protection, non-resident/index/compressed/encrypted/sparse state, fully mapped runlists, filename dirty state, deletion/creation, EA presence, and dirty runlists.
- `struct ntfs_attr` is a compact lookup key for attribute inodes, carrying MFT number, attribute name/type, name length, and state.

Concurrency and lifecycle:
- `size_lock` serializes inode size fields.
- `mrec_lock` protects the loaded MFT record for the inode.
- `extent_lock` protects extent inode attachment state.
- Runlist locking is delegated to `struct runlist` internals.

Exported interface:
- Inode lookup/allocation: `ntfs_iget`, `ntfs_attr_iget`, `ntfs_index_iget`, `ntfs_alloc_big_inode`, `ntfs_free_big_inode`, `ntfs_drop_big_inode`, `ntfs_evict_big_inode`.
- Initialization and mount-time load: `__ntfs_init_inode`, `ntfs_init_big_inode`, `ntfs_new_extent_inode`, `ntfs_clear_extent_inode`, `ntfs_read_inode_mount`.
- VFS operations: `ntfs_setattr`, `ntfs_getattr`, `ntfs_truncate_vfs`, `ntfs_set_vfs_operations`.
- MFT/extent/attribute maintenance: `ntfs_get_block_mft_record`, `__ntfs_write_inode`, `ntfs_inode_attach_all_extents`, `ntfs_inode_add_attrlist`, `ntfs_destroy_ext_inode`, `ntfs_inode_free_space`, `ntfs_inode_close`, `ntfs_inode_sync_filename`.
- Attribute I/O and initialization extension: `ntfs_inode_attr_pread`, `ntfs_inode_attr_pwrite`, `ntfs_extend_initialized_size`.
- Folio helper: `ntfs_get_locked_folio`.

Role in subsystem:
This is the central contract between NTFS metadata code, VFS inode operations, runlist mapping, iomap I/O, and MFT persistence. Most implementation files in this group consume `NTFS_I()` and the state helpers defined here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/iomap.c -->
# File Research: sources/os/linux/linux/fs/ntfs/iomap.c

This file implements the NTFS bridge to Linux iomap for buffered reads/writes, direct I/O mapping, page fault write mapping, zeroing, seek reporting, and writeback.

Read path:
- Resident attributes are mapped as `IOMAP_INLINE`: the resident value is copied from the MFT attribute record into a temporary zeroed page and released in `ntfs_read_iomap_end`.
- Non-resident attributes map file offsets through the NTFS runlist using `ntfs_attr_vcn_to_rl`.
- Holes, delayed allocation, mapped extents, and optionally unwritten extents are translated into `IOMAP_HOLE`, `IOMAP_DELALLOC`, `IOMAP_MAPPED`, or `IOMAP_UNWRITTEN`.
- The code treats NTFS initialized-size semantics carefully: NTFS has a single initialized boundary rather than arbitrary unwritten extent ranges. Seek operations request mapped behavior beyond initialized size so preallocated space is not misreported as a hole.

Zeroing and folio completion:
- `ntfs_iomap_put_folio_non_resident()` zeroes folio regions around `initialized_size` to prevent exposing stale disk/cache data when iomap zeroing touches beyond initialized data.
- `ntfs_iomap_valid()` checks whether a cached iomap still corresponds to a delayed allocation runlist entry; stale zero-range mappings cause `ntfs_zero_read_iomap_end()` to return `-EPERM`.
- `ntfs_dio_zero_range()` issues block-device zeroout for sector-aligned direct I/O ranges.

Write path:
- `__ntfs_write_iomap_begin()` rejects writes on shutdown volumes, expands attributes when writes exceed `data_size`, then dispatches resident or non-resident handling.
- Resident writes use inline iomap data copied from the resident attribute into a temporary page; `ntfs_write_iomap_end_resident()` copies modified bytes back into the MFT attribute and marks the MFT record dirty.
- Simple buffered non-resident writes can mark holes as `LCN_DELALLOC`, merge delayed-allocation runs into the runlist, hold dirty cluster accounting, and zero partial boundary clusters when needed.
- Delayed allocation/direct/page-mkwrite/writeback mapping is handled by `ntfs_write_da_iomap_begin_non_resident()`, which calls `ntfs_attr_map_cluster()` to allocate/map clusters and optionally update mapping pairs immediately for direct I/O, mkwrite, system files, or attribute inodes.
- Writes past `initialized_size` call `ntfs_extend_initialized_size()` before mapping, and page-mkwrite can update initialized size after mapping.

Exported operation tables:
- `ntfs_read_iomap_ops`
- `ntfs_write_iomap_ops`
- `ntfs_seek_iomap_ops`
- `ntfs_page_mkwrite_iomap_ops`
- `ntfs_dio_iomap_ops`
- `ntfs_writeback_ops`
- `ntfs_iomap_folio_ops`

Locking and error behavior:
- Runlist locks are taken for read/write around mapping and mutation.
- `mrec_lock` protects MFT attribute expansion and mapping-pair updates.
- Corrupt zero-length physical runs produce `-EIO`; invalid runlist states usually produce `-EINVAL` or `-EIO`; allocation/metadata failures propagate negative errno.
- The file is tightly coupled to `attrib.h`, `mft.h`, `inode.h`, `volume.h`, and Linux iomap/writeback APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/iomap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/iomap.h -->
# File Research: sources/os/linux/linux/fs/ntfs/iomap.h

This header declares the NTFS iomap integration points implemented in `iomap.c`.

Exports:
- `ntfs_write_iomap_ops`
- `ntfs_read_iomap_ops`
- `ntfs_seek_iomap_ops`
- `ntfs_page_mkwrite_iomap_ops`
- `ntfs_dio_iomap_ops`
- `ntfs_writeback_ops`
- `ntfs_iomap_folio_ops`
- `ntfs_dio_zero_range()`

Dependencies:
- Includes Linux `pagemap` and `iomap` APIs.
- Includes NTFS `volume.h` and `inode.h`.

Role in subsystem:
This is the public NTFS-local interface used by file operations, address-space operations, direct I/O paths, and writeback setup to access the iomap operation tables without depending on `iomap.c` internals.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/iomap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/layout.h -->
# File Research: sources/os/linux/linux/fs/ntfs/layout.h

This header is the NTFS on-disk format map for the driver. It defines packed structures, magic constants, enum flags, helper macros, and static size assertions for boot sectors, MFT records, attributes, filenames, security descriptors, indexes, reparse points, EAs, quotas, and related metadata.

Major definitions:
- Boot layout: `magicNTFS`, `struct bios_parameter_block`, and `struct ntfs_boot_sector`, with a 512-byte static assertion.
- Generic protected records: magic constants for `FILE`, `INDX`, `HOLE`, `RSTR`, `RCRD`, `CHKD`, `BAAD`, and empty records; helpers like `ntfs_is_file_recordp()` and `ntfs_is_rstr_recordp()`; `struct ntfs_record` for update sequence array metadata.
- System MFT records: `FILE_MFT`, `FILE_MFTMirr`, `FILE_LogFile`, `FILE_Volume`, `FILE_AttrDef`, `FILE_root`, `FILE_Bitmap`, `FILE_Boot`, `FILE_BadClus`, `FILE_Secure`, `FILE_UpCase`, `FILE_Extend`, and `FILE_first_user`.
- MFT records: `MFT_RECORD_*` flags, MFT reference packing/unpacking macros, `struct mft_record`, and legacy `struct mft_record_old`.
- Attribute system: `AT_*` type codes, collation rules, attribute definition flags, `struct attr_def`, non-resident attribute flags, compression layout commentary, resident flags, and `struct attr_record`.
- File metadata: `FILE_ATTR_*` flags, NTFS timestamp semantics, `struct standard_information`, `struct attr_list_entry`, filename namespace constants, `MAXIMUM_FILE_NAME_LENGTH`, and `struct file_name_attr`.
- Object IDs and security: `struct guid`, `struct object_id_attr`, SID/RID constants, `struct ntfs_sid`, ACE types/flags/access masks, `struct ntfs_ace`, object ACE flags, `struct ntfs_acl`, security descriptor flags, and `struct security_descriptor_relative`.
- `$Secure` indexing: `struct sii_index_key`, `struct sdh_index_key`, and extensive notes on `$SDS`, `$SII`, and `$SDH`.
- Volume metadata: `VOLUME_*` flags and `struct volume_information`.
- Indexing: `SMALL_INDEX` / `LARGE_INDEX`, `LEAF_NODE` / `INDEX_NODE`, `struct index_header`, `struct index_root`, `struct index_block`, index entry flags, `struct index_entry_header`, and `struct index_entry`.
- Reparse and EA metadata: `struct reparse_index_key`, many `IO_REPARSE_TAG_*` constants, `struct reparse_point`, `struct ea_information`, `NEED_EA`, and `struct ea_attr`.
- Quotas: quota flag constants, `struct quota_control_entry`, predefined quota IDs, and `QUOTA_VERSION`.

Important characteristics:
- The file uses little-endian disk types throughout and marks disk structs `__packed`.
- It embeds many format constraints directly in comments: alignment, resident/non-resident rules, sorted list/index order, variable-length record termination, and Windows-version-specific fields.
- It provides no executable algorithms beyond small magic comparison helpers and MFT reference macros; its primary role is authoritative structure layout for parser and writer code.

Role in subsystem:
Every NTFS metadata reader/writer depends on this file. It is the schema foundation used by inode loading, attribute lookup, index traversal, LogFile validation, security/quota/reparse handling, and MFT record manipulation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/layout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/lcnalloc.c -->
# File Research: sources/os/linux/linux/fs/ntfs/lcnalloc.c

This file implements cluster allocation and deallocation against the NTFS volume LCN bitmap.

Freeing by runlist:
- `ntfs_cluster_free_from_rl_nolock()` clears bitmap runs for all non-negative LCNs in a supplied runlist while the caller holds the volume LCN bitmap write lock.
- It waits until free-cluster accounting is known, skips sparse/sentinel runs, clears `$Bitmap`, accumulates freed clusters, and increments volume free-cluster accounting.

Allocation:
- `ntfs_cluster_alloc()` allocates clusters from either the MFT zone or data zones and returns a new runlist.
- Inputs include starting VCN, count, preferred LCN, zone, extension-vs-hole behavior, contiguous requirement, and deallocation-purpose flag.
- The allocator:
  - Enters NOFS allocation context and takes `vol->lcnbmp_lock`.
  - Checks available free clusters, optionally subtracting dirty clusters.
  - Searches the bitmap in chunks mapped through the page cache.
  - Uses `vol->lcn_empty_bits_per_page` to skip full bitmap pages.
  - Supports an initial hint, current zone positions, two-pass zone search, and fallback across MFT/data zones.
  - Coalesces adjacent allocated clusters into runlist elements.
  - Marks bitmap folios dirty, updates free-cluster accounting, and updates zone cursors.
  - Shrinks the MFT zone when data allocation exhausts ordinary data zones.
  - Terminates returned runlists with `LCN_ENOENT` for extension allocation or `LCN_RL_NOT_MAPPED` for hole filling.
- `max_empty_bit_range()` helps locate the start of the longest zero-bit range within a bitmap buffer.

Rollback and error handling:
- Allocation failure after partial bitmap mutation triggers rollback via `ntfs_cluster_free_from_rl_nolock()`.
- Rollback failure marks the volume erroneous and instructs chkdsk through error logging.
- `-ENOSPC`, `-ENOMEM`, `-EIO`, and `-EINVAL` are returned as error pointers.

Deallocation:
- `__ntfs_cluster_free()` frees clusters described by an inode runlist from a starting VCN and optional count.
- It can use an existing attribute search context or map runlist fragments as needed.
- It clears real cluster bits in `$Bitmap`, skips sparse runs, tracks total logical freed clusters separately from real physical freed clusters, and updates free-cluster accounting.
- If discard is enabled, it issues aligned block discard for freed physical ranges after releasing the bitmap lock.
- On mid-free failure, it recursively calls itself in rollback mode to re-set bitmap bits for already freed clusters.

Locking:
- Allocation and freeing serialize bitmap mutation with `vol->lcnbmp_lock`.
- Freeing requires the inode runlist write lock on entry.
- NOFS allocation context avoids filesystem recursion during memory allocation.
- The allocator interacts with folio locking/mapping for `$Bitmap` pages.

Role in subsystem:
This is the physical space manager for NTFS writes, truncation, delayed allocation conversion, and metadata growth. It is directly consumed by attribute mapping/expansion code and indirectly by the iomap write path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/lcnalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/lcnalloc.h -->
# File Research: sources/os/linux/linux/fs/ntfs/lcnalloc.h

This header declares NTFS cluster allocation and deallocation APIs plus the allocation zone identifiers.

Key definitions:
- Zone constants: `MFT_ZONE` and `DATA_ZONE`, bounded by `FIRST_ZONE` and `LAST_ZONE`.
- `ntfs_cluster_alloc()` allocates physical clusters and returns a runlist.
- `__ntfs_cluster_free()` is the lower-level free routine with rollback-mode support.
- `ntfs_cluster_free()` is the normal inline wrapper around `__ntfs_cluster_free(..., false)`.
- `ntfs_cluster_free_from_rl_nolock()` frees clusters from an already locked volume bitmap context.
- `ntfs_cluster_free_from_rl()` wraps the nolock variant with NOFS context and `vol->lcnbmp_lock`.

Important contract:
- `ntfs_cluster_free()` requires the target inode runlist to be write locked and the volume LCN bitmap lock to be unlocked on entry.
- The function may map unmapped runlist fragments using an attribute search context.
- It does not modify the caller’s runlist after freeing clusters; callers must later remove or mark freed runs.
- If a supplied search context becomes invalid, callers must check `IS_ERR(ctx->mrec)` and reinitialize or release the context.

Role in subsystem:
This header exposes the allocator/freeing contract to attribute, truncate, and metadata update code while centralizing locking expectations and rollback caveats.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/lcnalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/logfile.c -->
# File Research: sources/os/linux/linux/fs/ntfs/logfile.c

This file validates and empties the NTFS `$LogFile` journal during mount/recovery-related handling. It checks restart pages and writes an empty journal pattern when the log is known clean.

Validation helpers:
- `ntfs_check_restart_page_header()` validates restart page magic context, system/log page sizes, restart page position, LogFile version 1.1, USA count/offset, restart area offset, and `chkdsk_lsn` usage.
- `ntfs_check_restart_area()` validates restart-area bounds, client array offset/alignment, list indexes, restart length, sequence-number bit calculation from file size, and log record header/data offsets.
- `ntfs_check_log_client_array()` walks free and in-use client lists, detects loops/overflow, and validates first-entry previous links.
- `ntfs_check_and_load_restart_page()` combines those checks, copies the full restart page, applies MST deprotection when needed, optionally checks active log clients, and returns the current LSN from either `RSTR` or `CHKD`.

`ntfs_check_logfile()`:
- Treats an already marked empty LogFile as clean.
- Bounds LogFile size to `MaxLogFileSize`, aligns it to the selected log page size, and verifies the minimum size of two restart pages plus `MinLogRecordPages`.
- Scans plausible page-aligned restart page locations rather than byte-scanning.
- Distinguishes empty pages, log record pages, restart pages, and chkdsk-modified restart pages.
- Loads up to two valid restart pages and chooses the one with the greater LSN.
- Returns the selected restart page to the caller when requested; caller must `kvfree()` it.
- Marks the volume LogFile-empty flag if the whole journal appears empty.

`ntfs_empty_logfile()`:
- Assumes prior consistency checking and clean journal state.
- Truncates LogFile page cache, maps the LogFile runlist, allocates a cluster-sized `0xff` buffer, and writes it over every mapped cluster in the initialized LogFile range.
- Handles unmapped runlist fragments by remapping and restarting from the relevant VCN.
- Uses block-device readahead and waits for the first writeback range to catch serious I/O errors.
- On success, truncates the page cache again and marks `NVolLogFileEmpty`.
- On runlist corruption or I/O failure, marks volume errors and returns false.

Role in subsystem:
The Linux NTFS driver does not replay arbitrary journal records here; it verifies restart-page consistency and can empty a clean journal. This protects mounts from dirty/unsupported LogFile states and avoids reprocessing an already emptied log.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/logfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/logfile.h -->
# File Research: sources/os/linux/linux/fs/ntfs/logfile.h

This header defines the on-disk `$LogFile` restart structures and declares journal validation/emptying functions.

Constants:
- `MaxLogFileSize`: maximum supported LogFile size.
- `DefaultLogPageSize`: default 4096-byte log page size.
- `MinLogRecordPages`: minimum required log record pages after the restart pages.
- `LOGFILE_NO_CLIENT`: sentinel for no log client record.

Structures:
- `struct restart_page_header` describes the `RSTR`/`CHKD` restart page header, including USA metadata, system/log page sizes, restart area offset, and LogFile version fields.
- `struct restart_area` stores current LSN, log client list heads, clean-volume flags, sequence-number bit count, restart area/client array sizes, usable log file size, log record header/data offsets, and restart open count.
- `struct log_client_record` stores per-client oldest/restart LSNs, linked-list indexes, sequence number, and client name. For NTFS, the expected client is `"NTFS"`.

Flags:
- `RESTART_VOLUME_IS_CLEAN` marks clean shutdown state in newer Windows behavior.
- `RESTART_SPACE_FILLER` is a width filler.

Exported functions:
- `ntfs_check_logfile()` validates the journal and can return the current restart page.
- `ntfs_empty_logfile()` fills the journal with empty bytes after it has been deemed clean.

Role in subsystem:
This header provides the exact disk layout consumed by `logfile.c` and imported through `layout.h` magic/MST definitions. It is mount-time metadata infrastructure rather than general file I/O.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/logfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/malloc.h -->
# File Research: sources/os/linux/linux/fs/ntfs/malloc.h

This header provides small NTFS-local memory allocation wrappers.

Functions:
- `__ntfs_malloc(size, gfp_mask)` allocates page-sized-or-larger memory:
  - For `size <= PAGE_SIZE`, it uses `kmalloc(PAGE_SIZE, gfp_mask & ~__GFP_HIGHMEM)`.
  - For larger sizes below total RAM pages, it uses `__vmalloc(size, gfp_mask)`.
  - Returns `NULL` when the request is too large or allocation fails.
- `ntfs_malloc_nofs(size)` calls `__ntfs_malloc()` with `GFP_NOFS | __GFP_HIGHMEM`.
- `ntfs_malloc_nofs_nofail(size)` adds `__GFP_NOFAIL`.
- `ntfs_free(addr)` releases memory with `kvfree()`, matching either kmalloc or vmalloc backing.

Important behavior:
- Allocations are page-rounded by implementation behavior and intentionally avoid filesystem recursion through `GFP_NOFS`.
- The small-allocation path always allocates one full page, not the exact requested byte count.
- `BUG_ON(!size)` catches zero-sized allocations on the small path.

Role in subsystem:
This is a convenience layer for NTFS metadata buffers that may be backed by either slab or vmalloc memory and can be freed uniformly with `kvfree()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/malloc.h -->