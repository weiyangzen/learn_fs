# Group Research: group_1044_linux_stable_sources_os_linux_linux_stable_fs_ntfs_inode_h_sources__1fa2743f3731

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/inode.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/inode.h

## Summary
Defines the Linux NTFS in-memory inode model and the inode/attribute lifecycle API shared by the NTFS driver. It bridges VFS `struct inode` objects, NTFS MFT records, fake attribute inodes, extent records, runlists, attribute lists, index metadata, compression metadata, and delayed allocation state.

## Main Contents
- `enum ntfs_inode_mutex_lock_class` lockdep classes for parent/child inode, extension, and EA mutex nesting.
- `struct ntfs_inode`, the main per-NTFS-inode state container.
- `NI_*` state bits plus generated `NIno*`, `NInoSet*`, `NInoClear*`, `NInoTestSet*`, and `NInoTestClear*` helpers.
- `struct big_ntfs_inode`, `NTFS_I()`, and `VFS_I()` for embedding NTFS inode state inside VFS inodes.
- `struct ntfs_attr`, the key used by `iget` paths for named/fake attribute inodes.

## Key Interfaces
Declares inode lookup and allocation helpers (`ntfs_iget()`, `ntfs_attr_iget()`, `ntfs_index_iget()`, `ntfs_alloc_big_inode()`), eviction/drop/free paths, mount-time inode loading, truncate/setattr/getattr operations, MFT writeback, extent attachment/destruction, attribute pread/pwrite, initialized-size extension, operation-table setup, and locked-folio acquisition.

## Important Details
`struct ntfs_inode` is polymorphic. For real inodes it describes the base or extent MFT record; for fake attribute inodes `NI_Attr` is set and `type/name/name_len` describe the represented attribute while `ext.base_ntfs_ino` points back to the owning base inode. `nr_extents` distinguishes base records with loaded extents from extent/fake inodes.

The inode tracks both on-disk values (`mft_no`, sequence number, file flags, sizes, timestamps, attribute-list data, MFT record pointer) and runtime state (`runlist`, locks, folio offset, MFT LCN mapping, delayed cluster count, symlink target).

## Risks
Many consumers depend on the state-bit protocol and the fake-inode/base-inode distinction. Lock ordering is explicit but fragile around `mrec_lock`, `size_lock`, `runlist.lock`, and `extent_lock`. The comment notes dirty MFT records are still tied to inode lifetime rather than an independent dirty-record list.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/iomap.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/iomap.c

## Summary
Implements NTFS iomap operations for buffered reads/writes, direct I/O, page faults, seeking, zeroing, and writeback. It maps resident attributes as inline data and non-resident attributes through NTFS runlists, including delayed allocation and initialized-size handling.

## Main Responsibilities
- Provide exported `iomap_ops` tables for read, write, seek, page-mkwrite, and direct-I/O paths.
- Provide `ntfs_writeback_ops` and NTFS folio write operations.
- Convert NTFS resident attributes to `IOMAP_INLINE` buffers.
- Convert non-resident runlist entries into mapped, hole, delalloc, or unwritten iomaps.
- Expand attributes and initialized size before writes when needed.
- Allocate or convert delayed extents during write, fault, DIO, and writeback mapping.
- Zero partial clusters or folio regions that could expose uninitialized bytes.

## Key APIs
- `ntfs_read_iomap_ops`, `ntfs_write_iomap_ops`, `ntfs_seek_iomap_ops`.
- `ntfs_page_mkwrite_iomap_ops`, `ntfs_dio_iomap_ops`.
- `ntfs_writeback_ops`.
- `ntfs_iomap_folio_ops`.
- `ntfs_dio_zero_range()`.

## Important Behavior
Resident reads and writes allocate a temporary page, copy the resident attribute value from the MFT record, expose it as `IOMAP_INLINE`, then copy written inline data back to the resident attribute and dirty the MFT record.

Non-resident reads map VCNs through the runlist. For normal reads, bytes beyond `initialized_size` can be reported as `IOMAP_UNWRITTEN`; seek and zero paths deliberately treat preallocated NTFS space as mapped because NTFS models unwritten state as a single `initialized_size` boundary rather than per-extent unwritten records.

Buffered writes can first mark holes as `LCN_DELALLOC`, hold dirty-cluster accounting, and later call `ntfs_attr_map_cluster()` to allocate real clusters. Direct I/O and page-mkwrite paths allocate/update mapping immediately and zero edge clusters with block zeroout when newly allocated space is partially covered.

## State and Synchronization
The code coordinates `mrec_lock`, `runlist.lock`, NTFS volume shutdown state, dirty-cluster accounting, `i_dealloc_clusters`, `allocated_size`, `data_size`, and `initialized_size`. Cached iomaps for zeroing are validated against the runlist so stale delayed-allocation mappings do not zero data that has since been written.

## Risks
Correctness depends on not exposing data beyond `initialized_size`, especially around partial-cluster writes, stale iomaps, and transitions from holes to delayed or real allocations. Several paths unlock `mrec_lock` inside lower helpers, so callers must preserve the expected lock protocol. Resident inline mappings use temporary pages stored in `iomap->private`, making begin/end pairing mandatory.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/iomap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/iomap.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/iomap.h

## Summary
Declares the NTFS iomap integration surface used by the rest of the driver.

## Main Contents
Includes Linux pagemap/iomap headers plus NTFS volume and inode declarations, then exports the NTFS iomap operation tables for writes, reads, seeks, page-mkwrite, direct I/O, writeback, folio operations, and device zeroing.

## Key Interfaces
- `ntfs_write_iomap_ops`.
- `ntfs_read_iomap_ops`.
- `ntfs_seek_iomap_ops`.
- `ntfs_page_mkwrite_iomap_ops`.
- `ntfs_dio_iomap_ops`.
- `ntfs_writeback_ops`.
- `ntfs_iomap_folio_ops`.
- `ntfs_dio_zero_range()`.

## Risks
This header exposes shared operation-table symbols only; behavioral correctness depends on callers selecting the correct table for buffered I/O, DIO, seek, page fault, or writeback semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/iomap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/layout.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/layout.h

## Summary
Defines NTFS on-disk structures, constants, magic values, flags, indexes, security formats, quota records, reparse records, and extended-attribute records. This is the central schema header used when parsing or constructing NTFS metadata.

## Main Contents
- Boot-sector and BIOS parameter block structures.
- NTFS record magic values and helpers for `FILE`, `INDX`, `RSTR`, `RCRD`, `CHKD`, `BAAD`, `HOLE`, and empty records.
- Common multi-sector-transfer protected record header.
- System MFT record numbers and MFT reference packing/unpacking helpers.
- Current and old MFT record headers.
- Attribute type codes, attribute definition entries, attribute flags, resident/non-resident `struct attr_record`, and compression model notes.
- Standard information, attribute-list, file-name, GUID, and object-ID structures.
- Security identifiers, ACE/ACL/security descriptor structures, access masks, inheritance flags, and descriptor control flags.
- `$Secure` index keys, volume information flags, index headers/root/block/entry structures.
- Reparse, quota, EA-information, and packed EA structures.

## Important Behavior
The header is declarative but encodes many invariants used by parser code: packed little-endian layout, 8-byte alignment requirements for many variable records, MFT references as 48-bit record numbers plus 16-bit sequence numbers, update sequence array limits within the first 512-byte sector, and index entry trailing VCN placement.

Attribute records distinguish resident values embedded in the MFT record from non-resident values described by mapping pairs and VCN ranges. File and directory names are represented by resident `$FILE_NAME` attributes and directory index entries. Security descriptors are de-duplicated in `$Secure` through `$SII` and `$SDH` indexes.

## Cross-File Role
`logfile.h` and `logfile.c` use the record magic and common record protection definitions. Inode, attribute, index, MFT, directory, security, reparse, and EA code depend on this header for exact on-disk field offsets and flag values.

## Risks
Any drift between these packed structures and NTFS disk format corrupts parsing or writeback. Many structures contain variable-length tails, so callers must bounds-check lengths, offsets, alignment, and endian conversion before dereferencing embedded data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/layout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/lcnalloc.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/lcnalloc.c

## Summary
Implements NTFS cluster allocation and deallocation against the volume LCN bitmap. It manages MFT/data allocation zones, free-cluster accounting, dirty-cluster reservations, runlist construction, rollback, and optional discard on free.

## Main Responsibilities
- Free all real clusters described by a runlist with the LCN bitmap lock already held.
- Allocate clusters from the MFT zone or data zones while respecting hints, contiguity requests, and current zone cursors.
- Scan bitmap folios for free bits and coalesce allocated bits into runlist elements.
- Shrink the reserved MFT zone when data allocation exhausts normal data zones.
- Free clusters from an inode runlist, mapping unmapped fragments when needed.
- Roll back partial allocation/free failures and mark the volume erroneous if rollback fails.

## Key APIs
- `ntfs_cluster_free_from_rl_nolock()`.
- `ntfs_cluster_alloc()`.
- `__ntfs_cluster_free()`.
- `max_empty_bit_range()` as a local bitmap scan accelerator.

## Important Behavior
`ntfs_cluster_alloc()` waits until free-cluster accounting is known, takes `vol->lcnbmp_lock`, accounts for dirty delayed allocations unless allocating for deallocation, scans the requested zone(s), sets free bitmap bits to allocated, decrements free-cluster counters, updates `lcn_empty_bits_per_page`, and returns a terminated runlist. Termination differs by allocation purpose: extension runlists end with `LCN_ENOENT`, hole-filling runlists with `LCN_RL_NOT_MAPPED`.

The allocator treats the MFT zone separately from data zone 1 and data zone 2. It starts from caller hints or persisted zone positions, does wraparound passes within zones, switches zones as needed, and can halve the MFT zone to make space for data allocations.

`__ntfs_cluster_free()` clears bitmap runs, increments free-cluster accounting, supports sparse runs, maps unmapped runlist fragments, and optionally issues discard aligned to device granularity after successful frees.

## State and Synchronization
Uses `memalloc_nofs_save()`, `vol->lcnbmp_lock`, the `$Bitmap` inode mapping, bitmap folio locking/kmap, `free_clusters`, `dirty_clusters`, zone cursor fields, `lcn_empty_bits_per_page`, and the caller-held inode runlist write lock for inode-based frees.

## Risks
The allocator mutates several pieces of persistent and in-memory allocation state together; partial failures require rollback while still holding the bitmap lock. A failed rollback explicitly leaves inconsistent metadata and sets the volume error flag. Zone switching and bitmap-page accounting are subtle, especially when allocation starts from a hint or when the MFT zone is shrunk.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/lcnalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/lcnalloc.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/lcnalloc.h

## Summary
Declares NTFS cluster allocation/deallocation interfaces and zone identifiers.

## Main Contents
- Zone constants `MFT_ZONE` and `DATA_ZONE`, with boundary sentinels.
- `ntfs_cluster_alloc()` for bitmap-backed cluster allocation.
- `__ntfs_cluster_free()` and inline `ntfs_cluster_free()` for freeing clusters from an inode runlist.
- `ntfs_cluster_free_from_rl_nolock()` and inline `ntfs_cluster_free_from_rl()` for freeing all real clusters in a runlist.

## Important Details
The header documents lock requirements for deallocation in detail. `ntfs_cluster_free()` requires the inode runlist write lock and may map missing runlist fragments. `ntfs_cluster_free_from_rl()` saves NOFS allocation context, takes `vol->lcnbmp_lock`, calls the nolock helper, then restores context.

## Risks
Callers must not assume `ntfs_cluster_free()` edits the runlist; it only updates the LCN bitmap and accounting, leaving runlist removal or sparse marking to the caller. If a search context is passed, its saved pointers may point to new memory after the call and must be refreshed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/lcnalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/logfile.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/logfile.c

## Summary
Implements NTFS `$LogFile` restart-page validation and clean-log emptying. It verifies restart-page headers, restart areas, log client arrays, selects the newest valid restart page, and can overwrite a clean LogFile with `0xff` bytes.

## Main Responsibilities
- Validate restart page size, position, version, update sequence array, restart area offset, and chkdsk marker rules.
- Validate restart-area bounds, client-array bounds, sequence-number bits, and alignment fields.
- Validate free/in-use log client linked lists for bounds and loops.
- Load and multi-sector-transfer deprotect complete restart pages.
- Search the LogFile for restart pages and choose the most recent valid page by LSN.
- Empty a clean LogFile by writing `0xff` over mapped non-hole clusters.

## Key APIs
- `ntfs_check_logfile()`.
- `ntfs_empty_logfile()`.
- Internal validation helpers: `ntfs_check_restart_page_header()`, `ntfs_check_restart_area()`, `ntfs_check_log_client_array()`, `ntfs_check_and_load_restart_page()`.

## Important Behavior
Only LogFile version 1.1 is supported. Validation focuses on restart pages and does not replay or fully validate log record pages. Empty LogFiles are accepted and marked with `NVolLogFileEmpty`. If two restart pages are present, the one with the higher current/chkdsk LSN is kept.

`ntfs_empty_logfile()` assumes the journal has already been checked and found clean. It truncates cached LogFile pages, maps runlist fragments as needed, skips holes, writes a cluster-sized `0xff` buffer directly to the block device for each real cluster, waits for the first write range to catch serious I/O errors, and then marks the volume LogFile-empty.

## State and Synchronization
Uses the LogFile inode mapping, `NVolLogFileEmpty`, runlist write locking, `size_lock` for initialized size, block-device mapping readahead, direct block-device writes, and volume error flags.

## Risks
The checker intentionally ignores log record replay, so mount decisions depend on restart-page cleanliness rather than full transaction recovery. Emptying during mount bypasses normal attribute write helpers; runlist corruption or write failure sets volume errors and instructs chkdsk.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/logfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/logfile.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/logfile.h

## Summary
Defines NTFS `$LogFile` restart-page, restart-area, and log-client on-disk structures plus the public LogFile validation/emptying API.

## Main Contents
- LogFile sizing constants: `MaxLogFileSize`, `DefaultLogPageSize`, and `MinLogRecordPages`.
- `struct restart_page_header` for `RSTR`/`CHKD` restart pages.
- `LOGFILE_NO_CLIENT` constants.
- restart-area flags including `RESTART_VOLUME_IS_CLEAN`.
- `struct restart_area`.
- `struct log_client_record`.
- Declarations for `ntfs_check_logfile()` and `ntfs_empty_logfile()`.

## Important Details
The comments document the circular LogFile layout, dual restart pages, version expectations, Windows clean/dirty interpretations, client list conventions, restart-area alignment rules, and the fixed NTFS log client name. The driver expects one log client and supports version 1.1 semantics.

## Risks
Many fields are interpreted only after bounds and update-sequence validation in `logfile.c`; direct consumers must not trust offsets, lengths, or client indices without those checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/logfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/malloc.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/malloc.h

## Summary
Provides small NTFS memory allocation wrappers for page-multiple allocations in filesystem contexts.

## Main Contents
- `__ntfs_malloc()` allocates one page via `kmalloc()` for sizes up to `PAGE_SIZE`, otherwise uses `__vmalloc()` when the requested page count is below total RAM pages.
- `ntfs_malloc_nofs()` applies `GFP_NOFS | __GFP_HIGHMEM`.
- `ntfs_malloc_nofs_nofail()` adds `__GFP_NOFAIL`.
- `ntfs_free()` releases memory with `kvfree()`.

## Important Behavior
Allocations are rounded conceptually to page multiples and are intended for NTFS code paths where filesystem reclaim recursion must be avoided. Small allocations deliberately allocate a full page through `kmalloc(PAGE_SIZE, ...)`.

## Risks
`__ntfs_malloc()` `BUG_ON`s zero-size requests. The nofail wrapper inherits the implementation comment saying it guarantees success, but the underlying helper can still return `NULL` for requests whose page count is at least total RAM pages.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/malloc.h -->