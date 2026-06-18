# subset-b-005726 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/inode.h -->
## sources/distributed-fs/ceph-client/fs/ntfs/inode.h

### Purpose
`inode.h` defines the NTFS driver's private in-memory inode model and the exported inode lifecycle, lookup, writeback, truncate, attribute I/O, and initialized-size APIs used by the rest of `fs/ntfs`. It is the bridge between Linux VFS `struct inode` objects and NTFS-specific metadata such as MFT record number, attribute identity, runlists, MFT-record buffers, extent records, initialized size, allocation size, and NTFS state flags.

### Important APIs, Types, and Functions
The central type is `struct ntfs_inode`. It stores synchronization (`size_lock`, `mrec_lock`, `extent_lock`), persistent identity (`mft_no`, `seq_no`, `type`, `name`, `name_len`), volume linkage (`vol`), mapping state (`runlist`), on-disk size copies (`data_size`, `initialized_size`, `allocated_size`), resident MFT record state (`mrec`, `folio`, `folio_ofs`, `mft_lcn`, `mft_lcn_count`), attribute-list data, index/compression geometry, extent linkage, delayed-allocation accounting (`i_dealloc_clusters`), and symlink target storage.

`enum ntfs_inode_mutex_lock_class` provides lockdep classes for parent/child, extend, and EA locking paths. The `NI_*` bit enum describes inode state such as dirty MFT records, attribute-list presence, fake attribute inode status, MST protection, non-residency, index allocation presence, compressed/encrypted/sparse modes, full runlist mapping, filename dirtiness, deletion/creation, EA presence, and runlist dirtiness. `NINO_FNS` and `TAS_NINO_FNS` generate inline bit operations such as `NInoNonResident()`, `NInoSetDirty()`, and `NInoTestClearFileNameDirty()`.

`struct big_ntfs_inode` embeds `struct ntfs_inode` before the VFS inode; `NTFS_I()` and `VFS_I()` convert between the two. `struct ntfs_attr` is a compact key for iget/test/init paths for named streams and fake attribute inodes. Exported prototypes include inode acquisition (`ntfs_iget`, `ntfs_attr_iget`, `ntfs_index_iget`), allocation/free/eviction (`ntfs_alloc_big_inode`, `ntfs_free_big_inode`, `ntfs_evict_big_inode`), mount-time inode loading, setattr/getattr, MFT record lookup/writeback, extent attachment/destruction, initialized-size extension, attribute pread/pwrite, and VFS operation setup.

### Control Flow and State
The header establishes the normal flow for all NTFS inode users: a VFS inode is converted with `NTFS_I()`, state bits are tested to choose resident versus non-resident behavior, locks serialize access to mutable MFT/runlist/size fields, and exported helpers perform metadata lookup or mutation. Fake attribute inodes are identified with `NInoAttr()` and point back to the base inode through `ext.base_ntfs_ino`; real base inodes may own loaded extent inode arrays through `ext.extent_ntfs_inos`.

### State and Persistence Behavior
Most fields are cached copies of on-disk MFT or attribute-record state. `data_size`, `initialized_size`, `allocated_size`, `flags`, `i_crtime`, `attr_list`, and `runlist` mirror persistent NTFS structures and must stay synchronized with dirty-bit writeback paths. `NI_Dirty`, `NI_AttrListDirty`, `NI_FileNameDirty`, and `NI_RunlistDirty` mark metadata requiring persistence. The header does not perform persistence itself, but it defines the state consumed by MFT writeback, attribute expansion/truncation, iomap, and allocation code.

### Dependencies and Integration Points
This file depends directly on `debug.h` and Linux kernel types used transitively through the NTFS headers. It is included by the iomap, allocation, attribute, MFT, directory, and VFS layers. `NTFS_I()` is the common integration point for code that starts with VFS objects; `ntfs_extend_initialized_size()` is a key integration point for write paths; `ntfs_inode_attr_pread()` and `ntfs_inode_attr_pwrite()` expose attribute stream I/O to metadata consumers.

### Risks
The main risk is stale or inconsistently locked cached metadata. Callers must respect `size_lock`, `mrec_lock`, `runlist.lock`, and `extent_lock` or they can race truncation, writeback, allocation, or extent loading. Fake attribute inodes share base-record state, so lock ordering and `base_ntfs_ino` handling are critical. State bits are plain bit flags; setting a dirty bit without later writeback, or clearing it too early, risks persistent metadata loss.

### Test Signals
Useful signals include mount/read tests for base and extent MFT records, alternate data stream lookup, resident and non-resident file I/O, truncation and initialized-size extension, hard-link/name dirty writeback, EA and reparse attributes, and lockdep coverage for parent/child inode operations. Compile-time coverage should catch prototype drift through users of `NTFS_I()`, `VFS_I()`, and the exported inode APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/iomap.c -->
## sources/distributed-fs/ceph-client/fs/ntfs/iomap.c

### Purpose
`iomap.c` adapts NTFS resident and non-resident attribute storage to Linux's iomap read, buffered write, mmap write-fault, direct-I/O, zero-range, and writeback paths. It maps NTFS runlist entries and resident attribute values into `struct iomap` extents, handles delayed allocation and real cluster allocation, zeroes unwritten or partially initialized regions, and updates resident attribute data after inline writes.

### Important APIs, Types, and Functions
The file exports operation tables: `ntfs_read_iomap_ops`, `ntfs_write_iomap_ops`, `ntfs_seek_iomap_ops`, `ntfs_page_mkwrite_iomap_ops`, `ntfs_dio_iomap_ops`, `ntfs_writeback_ops`, and `ntfs_iomap_folio_ops`. `ntfs_dio_zero_range()` issues sector-aligned block-device zeroout for direct-I/O allocation edges.

Read mapping is split between `ntfs_read_iomap_begin_resident()` for resident attributes and `ntfs_read_iomap_begin_non_resident()` for runlist-backed attributes. Resident reads copy the attribute value into a temporary page and return `IOMAP_INLINE`; `ntfs_read_iomap_end()` releases that page. Non-resident reads translate file offsets to VCNs and LCNs, use `ntfs_attr_vcn_to_rl()`, return `IOMAP_HOLE`, `IOMAP_DELALLOC`, `IOMAP_MAPPED`, or conditionally `IOMAP_UNWRITTEN`, and clamp mappings around `initialized_size`.

Write mapping flows through `__ntfs_write_iomap_begin()`. For non-resident files, `ntfs_write_iomap_begin_non_resident()` may first expand the attribute and extend initialized size. `ntfs_write_simple_iomap_begin_non_resident()` marks holes as `LCN_DELALLOC` for buffered writes, reserves dirty clusters, merges runlists, and zeroes edge clusters when exposure would cross initialized data. `ntfs_write_da_iomap_begin_non_resident()` calls `ntfs_attr_map_cluster()` to allocate real clusters for delayed allocation, direct I/O, mmap write faults, or writeback. Resident writes use `ntfs_write_iomap_begin_resident()` and `ntfs_write_iomap_end_resident()` to copy inline data through a temporary page and back into the MFT attribute record.

Zeroing and validation use `ntfs_zero_range()`, `ntfs_zero_read_iomap_ops`, `ntfs_zero_iomap_folio_ops`, and `ntfs_iomap_valid()`. `ntfs_iomap_valid()` rejects stale cached iomaps if the runlist no longer contains `LCN_DELALLOC` at the mapped VCN.

### Control Flow and State
Read control flow first checks `NInoNonResident()`. Resident attributes are looked up under an NTFS attribute search context and represented as a single inline extent. Non-resident attributes are mapped under `ni->runlist.lock`, with `IOMAP_REPORT` returning `-ENOENT` for holes to support FIEMAP/seek-style reporting.

Write control flow starts by rejecting shutdown volumes, expanding attributes beyond `data_size`, and selecting resident or non-resident handling. Non-resident buffered writes can create delayed-allocation runlist elements and increment `ni->i_dealloc_clusters`; direct-I/O, mmap, and writeback paths allocate real clusters immediately through `ntfs_attr_map_cluster()`. Writeback reuses `wpc->iomap` until the folio range falls outside it, then remaps using `NTFS_IOMAP_FLAGS_WRITEBACK`.

### State and Persistence Behavior
This file mutates in-memory runlists, delayed allocation state, dirty cluster reservations, initialized size, and resident attribute bytes. Persistent metadata updates are delegated to attribute and MFT helpers such as `ntfs_attr_expand()`, `ntfs_attr_map_cluster()`, `ntfs_attr_set_initialized_size()`, and `mark_mft_record_dirty()`. Zeroing behavior is persistence-sensitive: before exposing newly allocated or previously uninitialized cluster edges, the code zeroes buffered folios or issues block-device zeroout for direct-I/O paths.

### Dependencies and Integration Points
It depends on Linux `iomap`, folio, writeback, and block-device zeroout APIs plus NTFS `attrib.h`, `mft.h`, `ntfs.h`, and `iomap.h`. It integrates with VFS address-space operations through exported iomap operation tables, with the allocator through delayed/real cluster states (`LCN_DELALLOC`, `LCN_HOLE`, LCN values), with inode state through `initialized_size` and `i_dealloc_clusters`, and with MFT writeback for resident data.

### Risks
The largest risks are stale cached iomaps, initialized-size boundary mistakes, and delayed-allocation accounting errors. A stale runlist while `iomap_zero_range()` iterates can zero data written through another path, which is why `ntfs_iomap_valid()` exists. Partial-cluster writes before `initialized_size` require edge zeroing; missed zeroing could expose stale disk contents. Locking is subtle: several error paths unlock `mrec_lock` after runlist operations, and direct/writeback flags control whether allocation updates mapping pairs immediately. The file also assumes resident inline iomaps are backed by temporary pages that are always released on end paths.

### Test Signals
High-value tests include buffered writes into holes, writes crossing `initialized_size`, direct-I/O writes with unaligned cluster edges but sector-aligned zeroout, mmap page faults beyond initialized size, writeback of delayed allocations, SEEK_DATA/SEEK_HOLE behavior over preallocated ranges, resident file read/write, and races between zero-range, truncate, and buffered writes. Fault-injection should cover allocation failure after dirty-cluster reservation and runlist merge failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/iomap.h -->
## sources/distributed-fs/ceph-client/fs/ntfs/iomap.h

### Purpose
`iomap.h` is the public NTFS header for iomap integration. It declares the operation tables implemented in `iomap.c` and the direct-I/O zeroing helper used by NTFS write and allocation paths.

### Important APIs, Types, and Functions
The header exports `ntfs_write_iomap_ops`, `ntfs_read_iomap_ops`, `ntfs_seek_iomap_ops`, `ntfs_page_mkwrite_iomap_ops`, `ntfs_dio_iomap_ops`, `ntfs_writeback_ops`, and `ntfs_iomap_folio_ops`. It also declares `ntfs_dio_zero_range(struct inode *inode, loff_t offset, loff_t length)`, which zeros block-device sectors for direct-I/O allocation edge handling.

### Control Flow and State
The header does not implement control flow; it makes the NTFS iomap dispatch points visible to VFS/address-space setup code. Callers select an operation table based on read, write, seek, page-mkwrite, direct-I/O, or writeback context, and `iomap.c` owns the actual mapping and state mutation.

### State and Persistence Behavior
No state is stored here. The declared operation tables mutate persistent-related state indirectly through runlist allocation, initialized-size updates, dirty MFT records, and block zeroing in `iomap.c`.

### Dependencies and Integration Points
It includes Linux `pagemap.h` and `iomap.h`, then NTFS `volume.h` and `inode.h`. It is the narrow integration contract between NTFS inode setup and Linux iomap helpers.

### Risks
Risk is mostly API drift: changes in Linux iomap callback signatures or NTFS operation table names must be reflected here and in all users. Including both `volume.h` and `inode.h` can increase coupling; any circular include change should be checked carefully.

### Test Signals
Compile coverage from address-space operation setup is the primary signal. Runtime signals come from any NTFS read/write/direct-I/O/mmap/writeback test that exercises these exported tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/iomap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/layout.h -->
## sources/distributed-fs/ceph-client/fs/ntfs/layout.h

### Purpose
`layout.h` is the NTFS on-disk format map for this driver. It defines packed structures, constants, magic values, bit masks, and helper macros for boot sectors, MFT records, attributes, file names, security descriptors, indexes, quota records, reparse points, EAs, and LogFile record identification. It is the source of truth for interpreting little-endian NTFS metadata stored on disk.

### Important APIs, Types, and Functions
Key structures include `struct bios_parameter_block`, `struct ntfs_boot_sector`, `struct ntfs_record`, `struct mft_record`, `struct mft_record_old`, `struct attr_def`, `struct attr_record`, `struct standard_information`, `struct attr_list_entry`, `struct file_name_attr`, `struct guid`, `struct object_id_attr`, `struct ntfs_sid`, `struct ntfs_ace`, `struct ntfs_acl`, `struct security_descriptor_relative`, `struct sii_index_key`, `struct sdh_index_key`, `struct volume_information`, `struct index_header`, `struct index_root`, `struct index_block`, `struct reparse_index_key`, `struct quota_control_entry`, `struct index_entry_header`, `struct index_entry`, `struct reparse_point`, `struct ea_information`, and `struct ea_attr`.

Important enums and macros include `magic_*` record identifiers and `ntfs_is_*` helpers, system MFT record numbers (`FILE_MFT`, `FILE_LogFile`, `FILE_Bitmap`, `FILE_first_user`, etc.), MFT reference packing/unpacking (`MK_MREF`, `MREF`, `MSEQNO`, `MREF_LE`), attribute type codes (`AT_STANDARD_INFORMATION`, `AT_DATA`, `AT_INDEX_ROOT`, etc.), collation codes, attribute flags, file attribute flags, SID/RID constants, ACE and access-mask values, security descriptor flags, volume flags, index flags, quota flags, and reparse tags. The header uses `static_assert` for several fixed on-disk sizes.

### Control Flow and State
This header does not execute control flow, but its constants drive nearly every parser and validator in the NTFS implementation. Callers read packed little-endian fields from disk, convert them with `le*_to_cpu()`, check record magics through the helper macros, use offsets and lengths embedded in these structures to find variable data, and validate flags against masks. Structures such as `attr_record` branch conceptually on `non_resident`, while `index_entry` branches on `INDEX_ENTRY_END` and `INDEX_ENTRY_NODE`.

### State and Persistence Behavior
All structures describe persistent NTFS metadata. They are packed to match disk layout and many contain variable-length tails whose bounds must be validated by consumers. Persistent state represented here includes volume identity and geometry, cluster/MFT locations, MFT record allocation and sequence numbers, attribute extents and sizes, initialized size, Windows file flags, timestamps, directory B+ tree nodes, LogFile record magic, security descriptor indexes, quota state, reparse tags, and EA records.

### Dependencies and Integration Points
The header depends on kernel types, bit operations, lists, and byte-order definitions. It is included by `logfile.h` and many NTFS metadata consumers. `logfile.c` uses the magic helpers for `RSTR`, `RCRD`, `CHKD`, and empty records; inode, MFT, attribute, directory, security, and allocation code rely on the packed records and constants.

### Risks
The primary risk is ABI mismatch with disk. Any structure padding, missing `__packed`, wrong endian annotation, or incorrect size assumption can corrupt parsing or writes. Variable-length arrays and offset fields require strict bounds checks in consumers. Several definitions encode historical NTFS variants, so code must distinguish NTFS 1.x/3.x structures and Windows compatibility behavior. Security and reparse constants must be treated carefully because unsupported features may require read-only mounts or explicit rejection.

### Test Signals
Compile-time `static_assert`s catch some layout drift. Runtime signals should include mounting volumes with varied sector and cluster sizes, old and NTFS 3.1 MFT records, resident and non-resident attributes, attribute lists, directory indexes, security descriptor indexes, quota/reparse/EA attributes, dirty-volume flags, and malformed images with bad magic, impossible offsets, or truncated variable-length records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/lcnalloc.c -->
## sources/distributed-fs/ceph-client/fs/ntfs/lcnalloc.c

### Purpose
`lcnalloc.c` implements NTFS logical-cluster allocation and deallocation against the volume `$Bitmap` attribute. It allocates clusters from the MFT or data zones, updates allocation bitmap bits, maintains free/dirty cluster counters and allocator cursors, shrinks the MFT zone when necessary, frees clusters from runlists, and issues discard after successful frees when enabled.

### Important APIs, Types, and Functions
`ntfs_cluster_alloc()` is the main allocator. It takes a target VCN, requested count, optional LCN hint, allocation zone (`MFT_ZONE` or `DATA_ZONE`), extension versus hole-fill mode, contiguity requirement, and deallocation-reservation mode. It returns a newly allocated runlist or an error pointer.

`ntfs_cluster_free_from_rl_nolock()` frees every non-negative LCN run in a supplied runlist while the volume LCN bitmap lock is already held. `__ntfs_cluster_free()` frees a range from an inode runlist, maps unmapped runlist fragments as needed, rolls back on partial failure, updates free counts, and optionally discards freed block-device ranges. `max_empty_bit_range()` is a local scanner that finds the longest zero-bit run in a bitmap buffer when no caller hint is being followed.

### Control Flow and State
Allocation begins by validating arguments, entering NOFS allocation context, waiting until free-cluster accounting is known, taking `vol->lcnbmp_lock`, and checking free space minus dirty reservations. It chooses a starting zone based on caller hint or volume cursors (`mft_zone_pos`, `data1_zone_pos`, `data2_zone_pos`) and then scans `$Bitmap` folios. For each free bit it marks the bit allocated, dirties the folio, decrements free clusters, updates per-page empty-bit hints, and appends or coalesces a runlist element. If a zone is exhausted, the allocator performs a second pass over the skipped prefix, switches zones, or shrinks the MFT zone for data allocation. On success it appends a terminator with `LCN_ENOENT` for extension or `LCN_RL_NOT_MAPPED` for hole fill.

Freeing starts at a VCN, finds the corresponding runlist element, clears bitmap bits for real clusters, skips sparse holes, maps unmapped fragments as needed, and tracks both total VCNs processed and real clusters freed. On error after partial freeing, it recursively calls `__ntfs_cluster_free(..., is_rollback=true)` to restore bits and marks volume errors if rollback fails. After success it increments free cluster count and may issue `blkdev_issue_discard()` for aligned freed ranges.

### State and Persistence Behavior
This file directly mutates persistent allocation state in the `$Bitmap` inode's page cache and marks modified folios dirty. It updates in-memory volume accounting (`free_clusters`, `dirty_clusters`, zone cursors, MFT zone bounds, per-page empty-bit hints) to mirror allocation decisions. Rollback is designed to preserve on-disk bitmap consistency when allocation or free operations fail partway through; failure to roll back sets the volume error flag and instructs chkdsk.

### Dependencies and Integration Points
It depends on Linux block-device APIs plus NTFS `lcnalloc.h`, `bitmap.h`, and `ntfs.h`. It integrates with runlist mapping (`ntfs_attr_find_vcn_nolock()`), bitmap bit setters/clearers, volume flags (`NVolFreeClusterKnown`, `NVolDiscard`, `NVolSetErrors`), allocator accounting helpers (`ntfs_inc_free_clusters`, `ntfs_dec_free_clusters`, dirty-cluster helpers), and write paths that request delayed or real allocation.

### Risks
Allocation correctness depends on bitmap locking, folio dirtying, and runlist rollback. Incorrect zone cursor updates can cause fragmentation or missed free space; incorrect MFT zone shrinking can consume reserved MFT growth space too aggressively. Partial failure paths are high risk because bitmap bits may already be changed. The code also mixes byte, bit, cluster, sector, and page units, so off-by-one errors around `buf_size`, `zone_end`, and VCN/LCN conversions are important. Discard alignment must not discard outside freed extents.

### Test Signals
Useful tests include allocating in data and MFT zones, hinted allocations, contiguous-only allocation, ENOSPC with rollback, MFT-zone shrink behavior, freeing ranges that start/end mid-run, freeing sparse and unmapped runs, discard-enabled frees, dirty-cluster reservation interaction with writeback, and fault injection for bitmap read, memory allocation, and bitmap update failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/lcnalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/lcnalloc.h -->
## sources/distributed-fs/ceph-client/fs/ntfs/lcnalloc.h

### Purpose
`lcnalloc.h` declares the NTFS cluster allocation/deallocation interface and documents the locking contract for callers. It exposes allocation zones, the allocator entry point, the lower-level free routine, and convenience wrappers for freeing clusters from inode runlists or standalone runlists.

### Important APIs, Types, and Functions
The zone enum defines `MFT_ZONE` and `DATA_ZONE`, with `FIRST_ZONE` and `LAST_ZONE` aliases for validation. `ntfs_cluster_alloc()` allocates clusters and returns a runlist. `__ntfs_cluster_free()` is the full free implementation, including rollback mode. `ntfs_cluster_free()` is the normal inline wrapper with `is_rollback=false`. `ntfs_cluster_free_from_rl_nolock()` and `ntfs_cluster_free_from_rl()` free all concrete runs in a supplied runlist, with the latter taking and releasing the volume LCN bitmap lock.

### Control Flow and State
The header captures expected caller flow: hold the inode runlist lock for cluster-free operations, call allocation with the volume bitmap unlocked, and allow the implementation to take `vol->lcnbmp_lock`. For `ntfs_cluster_free_from_rl()`, callers must already stabilize the runlist while the wrapper handles bitmap locking and NOFS context.

### State and Persistence Behavior
The functions declared here mutate the persistent `$Bitmap` allocation map and volume free-space accounting in `lcnalloc.c`. The header's comments are persistence-relevant because they specify that `ntfs_cluster_free()` does not modify the inode runlist; callers must later remove or mark freed runs so runlist state and on-disk allocation state do not diverge.

### Dependencies and Integration Points
It includes `linux/sched/mm.h` for NOFS memory-allocation context and `attrib.h` for NTFS volume, inode, runlist, and attribute-search types. It is used by attribute expansion/truncation, delayed allocation, rollback, and metadata cleanup paths that need cluster ownership changes.

### Risks
The risk is misuse of locking or post-free runlist handling. Calling the free API without a write-locked runlist can race runlist mapping or truncation. Assuming the free API edits the runlist would leave stale mappings to freed clusters. Supplying an invalid `ctx` can leave `ctx->mrec` as an error pointer per the warning in the contract.

### Test Signals
Compile coverage should verify API signatures. Runtime signals include truncation, hole punching/sparse conversion if supported, allocation rollback, cluster free with and without an existing attribute search context, and lockdep checks for runlist and bitmap lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/lcnalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/logfile.c -->
## sources/distributed-fs/ceph-client/fs/ntfs/logfile.c

### Purpose
`logfile.c` validates the NTFS `$LogFile` journal restart pages during mount and can empty a clean log by overwriting its allocated clusters with `0xff`. The implementation focuses on restart-page consistency rather than full log replay; it verifies page geometry, update sequence array placement, restart-area bounds, log-client lists, and selects the newest valid restart page.

### Important APIs, Types, and Functions
The exported functions are `ntfs_check_logfile()` and `ntfs_empty_logfile()`. Internal validators include `ntfs_check_restart_page_header()`, `ntfs_check_restart_area()`, `ntfs_check_log_client_array()`, and `ntfs_check_and_load_restart_page()`.

`ntfs_check_restart_page_header()` validates page sizes, restart-page position, LogFile version 1.1, USA count/offset when present, restart-area offset, and `chkdsk_lsn` rules. `ntfs_check_restart_area()` validates client-array offset, restart-area length, free/in-use list heads, sequence-number bits derived from file size, and alignment of log-record and page-data offsets. `ntfs_check_log_client_array()` traverses free and in-use client linked lists to detect out-of-range indices and loops. `ntfs_check_and_load_restart_page()` copies the full restart page, applies MST fixups when needed, optionally validates clients, and returns a deprotected page plus its LSN.

### Control Flow and State
`ntfs_check_logfile()` first treats `NVolLogFileEmpty()` as already clean, caps the size to `MaxLogFileSize`, chooses a log page size, checks the file is large enough for two restart pages plus minimum log records, then scans candidate page boundaries. It distinguishes empty `0xff` pages, log-record pages, restart pages (`RSTR`), and chkdsk-modified pages (`CHKD`). It loads up to two valid restart pages and returns the one with the newer LSN. If the whole file is empty, it sets `NVolLogFileEmpty()`.

`ntfs_empty_logfile()` requires a previously checked clean log. It truncates `$LogFile` page cache, maps the `$LogFile` runlist, allocates a cluster-sized `0xff` buffer, writes it to each real cluster in initialized size, waits for the first write range to catch serious I/O errors, skips holes, and marks the volume log empty on success. On runlist or I/O errors it sets the volume error flag and asks for chkdsk.

### State and Persistence Behavior
Validation itself reads `$LogFile` pages and returns a heap copy of the selected restart page to the caller. Emptying mutates persistent journal storage by overwriting allocated clusters with `0xff`, invalidates page cache before and after, and sets the in-memory `NVolLogFileEmpty` flag. Errors can set persistent-volume error state through `NVolSetErrors()`.

### Dependencies and Integration Points
The file depends on Linux block/page-cache APIs plus NTFS `attrib.h`, `logfile.h`, and `ntfs.h`. It uses layout magic helpers for `RSTR`, `RCRD`, `CHKD`, and empty records, MST fixup through `post_read_mst_fixup()`, runlist mapping through `ntfs_map_runlist_nolock()`, and low-level block writes through `ntfs_bdev_write()`. It is part of mount-time journal/volume-cleanliness handling.

### Risks
The code supports only LogFile version 1.1, so newer or unusual versions are rejected unless handled elsewhere. It intentionally ignores log record pages beyond restart-page checks, so it does not provide full journal replay. Restart-page scanning depends on page-size assumptions and candidate offsets; malformed files could exercise bounds-sensitive paths. `ntfs_empty_logfile()` performs raw block writes while mounting, so runlist corruption or partial I/O failure risks metadata inconsistency and correctly escalates to volume errors.

### Test Signals
Useful tests include clean and dirty LogFile images, two restart pages with differing LSNs, CHKD restart pages without USA, unsupported page sizes or versions, corrupt client lists with loops, MST fixup failure, empty log detection, emptying logs with fragmented runlists, holes in `$LogFile`, and injected write failures that set volume errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/logfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/logfile.h -->
## sources/distributed-fs/ceph-client/fs/ntfs/logfile.h

### Purpose
`logfile.h` defines the NTFS `$LogFile` restart-page and restart-area structures, log-client records, constants, flags, and exported journal validation/emptying APIs used by `logfile.c` and mount code.

### Important APIs, Types, and Functions
Constants include `MaxLogFileSize`, `DefaultLogPageSize`, and `MinLogRecordPages`. `struct restart_page_header` models the `RSTR`/`CHKD` page header, including USA fields, page sizes, version, and restart-area offset. `LOGFILE_NO_CLIENT` and `LOGFILE_NO_CLIENT_CPU` mark absent log-client list links. `RESTART_VOLUME_IS_CLEAN` records clean shutdown state. `struct restart_area` stores current LSN, client-list heads, flags, sequence-number bits, restart-area length, client-array offset, file size, and log-page data geometry. `struct log_client_record` stores oldest/restart LSNs, linked-list pointers, sequence number, and client name. The exported APIs are `ntfs_check_logfile()` and `ntfs_empty_logfile()`.

### Control Flow and State
The header describes the two-restart-page layout followed by circular log-record pages. It does not implement flow, but `logfile.c` reads these structures in order: restart page header, restart area, then client records if the log is open and not chkdsk-modified.

### State and Persistence Behavior
All structures are packed persistent on-disk records in `$LogFile`. They encode whether the volume was shut down cleanly, where clients should restart, and the usable size and geometry of the log. The clean/dirty interpretation depends on both client-list state and `RESTART_VOLUME_IS_CLEAN`.

### Dependencies and Integration Points
The header includes `layout.h` for magic values and packed NTFS types. It is consumed by mount-time journal checking and by any code deciding whether the log can be emptied or the volume must be considered dirty.

### Risks
The documented compatibility note says the driver targets LogFile version 1.1; older or newer formats may not be safely interpreted. Any mismatch in packed layout or endian handling would break mount-time journal checks. Cleanliness logic is version- and Windows-behavior-sensitive, especially because Windows XP and later may keep the logfile open even after clean shutdown.

### Test Signals
Compile checks cover structure availability. Runtime image tests should include version 1.1 restart areas, clean and dirty flags, Win2k-style closed clients, XP-style open clean logs, CHKD-modified logs, and boundary values for page size, file size, and client-array offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/logfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/malloc.h -->
## sources/distributed-fs/ceph-client/fs/ntfs/malloc.h

### Purpose
`malloc.h` provides NTFS-specific memory allocation helpers that allocate in page-sized units and use NOFS allocation semantics for filesystem paths. It gives older NTFS code a small abstraction over `kmalloc`, `__vmalloc`, and `kvfree`.

### Important APIs, Types, and Functions
`__ntfs_malloc(size, gfp_mask)` allocates at least one page for small requests via `kmalloc(PAGE_SIZE, ...)` and larger requests via `__vmalloc()` if the request is smaller than total RAM pages. `ntfs_malloc_nofs(size)` adds `GFP_NOFS | __GFP_HIGHMEM`. `ntfs_malloc_nofs_nofail(size)` adds `__GFP_NOFAIL`. `ntfs_free(addr)` releases either allocation form through `kvfree()`.

### Control Flow and State
The allocation flow branches only on `size <= PAGE_SIZE`. Small nonzero allocations are rounded to a full page and use `kmalloc` with highmem stripped; larger allocations use vmalloc. There is no persistent state.

### State and Persistence Behavior
No filesystem metadata is changed. The persistence relevance is indirect: NOFS allocation avoids recursive filesystem reclaim while NTFS metadata paths hold locks or manipulate on-disk structures.

### Dependencies and Integration Points
It includes Linux `vmalloc.h`, `slab.h`, and `highmem.h`. It is intended for NTFS code paths that need page-multiple buffers and a common free function regardless of kmalloc/vmalloc backing.

### Risks
Small allocations always consume a full page, so using this helper for many tiny objects can waste memory. `BUG_ON(!size)` makes zero-size calls fatal. `ntfs_malloc_nofs_nofail()` can sleep indefinitely under memory pressure. The large allocation guard compares page count to `totalram_pages()` but does not guarantee practical vmalloc availability.

### Test Signals
Signals include compile coverage for callers, allocation-failure fault injection for non-nofail users, zero-size misuse detection in debug testing, and kmemleak/KASAN coverage that `ntfs_free()` correctly pairs with both allocation branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/malloc.h -->
