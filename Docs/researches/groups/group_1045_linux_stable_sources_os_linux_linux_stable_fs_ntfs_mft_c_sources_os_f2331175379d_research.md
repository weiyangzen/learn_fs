# Group Research: group_1045_linux_stable_sources_os_linux_linux_stable_fs_ntfs_mft_c_sources_os_f2331175379d

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/mft.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/mft.c

## Summary
Implements NTFS Master File Table record validation, mapping, dirtying, allocation, freeing, mirror synchronization, and `$MFT` writeback. This is the central mutation path for MFT records and the code that grows `$MFT` and `$MFT/$BITMAP` when new inodes are needed.

## Main Responsibilities
- Validate basic MFT record structure: `FILE` magic, USA/fixup fields, record size, in-use size, and attribute offset alignment.
- Map MFT records from the `$MFT` page cache into per-inode copied buffers and apply MST post-read fixups.
- Map and attach extent MFT records to base NTFS inodes.
- Mark MFT records dirty through the owning base VFS inode.
- Write single MFT records directly to the block device, applying MST pre-write fixups and syncing `$MFTMirr` when needed.
- Decide whether page-cache `$MFT` writeback may safely write records whose inode objects may or may not be in icache.
- Allocate new MFT records by scanning/extending `$MFT/$BITMAP`, extending `$MFT/$DATA`, formatting records, and setting in-use flags.
- Free MFT records by clearing in-use flags, advancing sequence numbers, writing records, and clearing bitmap bits.
- Provide `$MFT` address-space writeback via `ntfs_mft_writepages()` and `ntfs_mft_mark_dirty()`.

## Key Interfaces
- `ntfs_mft_record_check()`
- `map_mft_record()`, `unmap_mft_record()`, `map_extent_mft_record()`
- `__mark_mft_record_dirty()`
- `ntfs_sync_mft_mirror()`
- `write_mft_record_nolock()`
- `ntfs_mft_record_alloc()`
- `ntfs_mft_record_free()`
- `ntfs_mft_writepages()`
- `ntfs_mft_mark_dirty()`

## Important Behavior
MFT mapping reads the relevant folio from `$MFT`, copies the record into `ni->mrec`, applies MST fixups to the copy, validates it, and records the backing folio plus offset in the NTFS inode. `unmap_mft_record()` decrements the NTFS inode reference count; dirty data must be marked before unmapping.

Allocation avoids normal records below `RESERVED_MFT_RECORDS` except for special `$MFT` extent handling, scans bitmap bits from either the global allocation cursor or the base inode, and grows `$MFT/$BITMAP` by 8 initialized bytes at a time when needed. `$MFT/$DATA` allocation grows in chunks of roughly 16 records, falling back to the minimum one-record allocation.

When newly allocated records lie beyond initialized `$MFT` data, the file grows record-by-record and each record is formatted with `FILE` magic, USA metadata, sequence number, attribute offset, and an `AT_END` terminator. Allocated records are then marked in use and directories receive `MFT_RECORD_IS_DIRECTORY`.

Writeback is conservative. `ntfs_may_write_mft_record()` avoids writing records whose corresponding inode is dirty, being created, being deleted, or currently locked, and uses nonblocking inode lookup to avoid folio-lock/inode-lock deadlocks. `$MFT` writeback applies/synchronizes MST-protected records and writes through bios.

## Risks
This file coordinates bitmap state, runlists, MFT sizes, MFT record contents, inode cache state, mirror writes, and rollback paths. Many failure paths set `NVolErrors()` because partial rollback can leave metadata inconsistent. Lock ordering around `mrec_lock`, `mftbmp_lock`, runlist locks, inode references, and folio locks is central to avoiding deadlocks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/mft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/mft.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/mft.h

## Summary
Declares the NTFS MFT record mapping, dirtying, allocation, freeing, mirror-sync, writeback, and folio-dirtying interfaces.

## Main Contents
- MFT record map/unmap declarations.
- Extent record mapping helpers.
- `mark_mft_record_dirty()` inline wrapper around `NInoTestSetDirty()` and `__mark_mft_record_dirty()`.
- MFT mirror sync and record write declarations.
- MFT record allocation/free declarations.
- `$MFT` record-range write, validation, writepages, and dirty-folio declarations.

## Important Details
`write_mft_record()` locks the containing folio around `write_mft_record_nolock()` to serialize explicit record writes with page-cache writeback and read-folio paths. Dirty marking is intentionally skipped if the NTFS inode dirty bit was already set.

## Risks
Callers must follow the map/dirty/unmap protocol and must only pass mapped records to write paths. The header exposes low-level metadata mutation APIs where lock ownership and record lifetime are enforced by convention.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/mft.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/mst.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/mst.c

## Summary
Implements NTFS multi-sector transfer protection fixup handling for protected on-disk records such as MFT and index records.

## Main Interfaces
- `post_read_mst_fixup()`
- `pre_write_mst_fixup()`
- `post_write_mst_fixup()`

## Important Behavior
`post_read_mst_fixup()` validates the update sequence array layout and checks each protected sector trailer against the update sequence number. On mismatch, it marks the in-memory record magic as `BAAD` and returns `-EINVAL`; invalid or absent USA metadata is treated as not protected and succeeds.

`pre_write_mst_fixup()` increments the update sequence number, skipping `0` and `0xffff`, saves original sector trailer words into the USA, and writes the new sequence number into each protected sector trailer. Unlike post-read, invalid USA metadata returns `-EINVAL`.

`post_write_mst_fixup()` restores the original trailer words after a pre-write fixup without revalidating, for in-memory cleanup after write preparation.

## Risks
Correctness depends on exact 512-byte sector assumptions and valid USA offsets/counts. Pre-write fixups mutate the record buffer, so callers must restore or work on a disposable/writeback copy.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/mst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/namei.c

## Summary
Implements NTFS directory inode operations and NFS export helpers: lookup, create, unlink, mkdir, rmdir, rename, symlink, mknod, hard link, and parent lookup.

## Main Responsibilities
- Validate Windows-compatible names, including illegal characters, trailing dot/space, and reserved DOS device names when enabled.
- Resolve directory lookups with NTFS case-insensitive and DOS short-name semantics while keeping the Linux dcache case-sensitive.
- Create files, directories, WSL symlinks, and WSL special files by allocating MFT records and adding NTFS attributes.
- Add default security descriptors, standard information, file-name attributes, indexes, data attributes, EA metadata, and reparse data.
- Delete names from directory indexes and inode `AT_FILE_NAME` attributes while tracking link counts.
- Create hard links through new `AT_FILE_NAME` attributes and directory index entries.
- Implement rename as link-at-new-name followed by delete-old-name, with rollback attempt if old deletion fails.
- Provide NFS export parent and file-handle lookup support.

## Key Interfaces
- `ntfs_dir_inode_ops`
- `ntfs_export_ops`
- Internal helpers: `__ntfs_create()`, `ntfs_delete()`, `__ntfs_link()`, `ntfs_get_parent()`

## Important Behavior
Creation allocates a fresh MFT record, temporarily marks the inode `I_NEW | I_CREATING`, inserts it into the inode hash, creates core NTFS attributes, adds a POSIX namespace `FILE_NAME` attribute, and inserts that filename into the parent index. Directories get an `I30` index root; regular files get an unnamed `$DATA` attribute; Linux symlinks and special files are represented with WSL reparse tags and WSL EA metadata.

Lookup handles three NTFS naming cases: exact WIN32/POSIX match, case-insensitive WIN32 match requiring a properly cased alias dentry, and DOS short-name match requiring lookup of the corresponding WIN32 filename.

Deletion removes the directory index entry and `AT_FILE_NAME` attribute, decrements MFT link count, updates VFS nlink rules, and when the final link disappears marks the inode as being deleted and removes reparse/object-id index entries.

## Risks
Namespace operations update several metadata structures that must stay consistent: parent index entries, filename attributes, MFT link count, VFS link count, EA metadata, reparse indexes, object-id indexes, and timestamps. Rename is not an atomic metadata transaction and relies on best-effort rollback.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/ntfs.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/ntfs.h

## Summary
Central NTFS driver header with core constants, unit-conversion helpers, global operation-table declarations, slab cache declarations, and cross-module function declarations.

## Main Contents
- NTFS constants for default preallocation, compression unit, compression cluster limit, block size, magic, and name limits.
- Byte/cluster/page/MFT-record/sector conversion macros and inline helpers.
- Case-sensitivity constants.
- `NTFS_SB()` accessor.
- Externs for NTFS slab caches and VFS operation tables.
- Declarations for compression, superblock, MST, Unicode/name conversion, ioctl, upcase generation, and block-device I/O helpers.
- `ntfs_ffs()` local helper.

## Important Details
This file is a cross-subsystem include point tying volume, layout, and inode definitions into most NTFS C files. It exposes both macro and inline forms for core address translations.

## Risks
Any error in the conversion helpers affects block addressing, MFT record placement, page offsets, and cluster accounting across the driver.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/ntfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/object_id.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/object_id.c

## Summary
Handles removal of NTFS object ID index entries from `$Extend/$ObjId`.

## Main Responsibilities
- Define `$O` object-id index name and packed index key/data structures.
- Open `$Extend/$ObjId` by looking up `$ObjId` under the `$Extend` system directory.
- Read an inode’s `AT_OBJECT_ID` attribute.
- Remove the matching object ID key from the `$ObjId` index.

## Key Interface
- `ntfs_delete_object_id_index()`

## Important Behavior
The delete path opens the inode’s `AT_OBJECT_ID` fake attribute inode, opens the `$ObjId` index context, locks the index inode MFT record, removes the index entry if found, marks the index entry and MFT record dirty, then drops all references.

## Risks
The function only removes index state; broader object-id attribute removal is handled elsewhere. Failure to open `$ObjId` silently leaves `ret` as success, so missing system-index access can leave cleanup incomplete.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/object_id.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/object_id.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/object_id.h

## Summary
Declares the object-id index name and object-id index deletion helper.

## Main Contents
- `extern __le16 objid_index_name[]`
- `ntfs_delete_object_id_index()`

## Risks
This header exposes only the cleanup interface; callers must know when an inode’s object ID metadata should be unindexed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/object_id.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/quota.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/quota.c

## Summary
Marks NTFS quota metadata out of date so Windows can rescan and rebuild quota state.

## Key Interface
- `ntfs_mark_quotas_out_of_date()`

## Important Behavior
The function checks cached volume state, verifies quota inodes are open, locks `$Quota/$Q`, looks up the default quota entry in the `I30` index, validates the entry size and quota version, and sets `QUOTA_FLAG_OUT_OF_DATE` if quota tracking is enabled/requested or pending deletes exist. It marks the index entry dirty and sets the in-memory volume flag to avoid repeating the operation.

## Risks
Failures to locate or validate the quota default entry return false and log errors. The code assumes the mounted system quota inodes are already available.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/quota.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/quota.h

## Summary
Declares the NTFS quota out-of-date helper.

## Main Contents
- Includes `volume.h`.
- Declares `ntfs_mark_quotas_out_of_date()`.

## Risks
Minimal header; behavioral risk is entirely in callers deciding when quota metadata needs invalidation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/reparse.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/reparse.c

## Summary
Implements NTFS reparse-point validation, interpretation, indexing, creation, and deletion, with explicit support for WSL symlinks and WSL special files.

## Main Responsibilities
- Validate reparse buffers and tag-specific payloads.
- Convert reparse tags to Linux file modes or directory-entry types.
- Load WSL symlink targets into `ni->target`.
- Open `$Extend/$Reparse` and maintain its `$R` index.
- Add, update, and remove `AT_REPARSE_POINT` data.
- Create WSL LX symlink reparse data.
- Create WSL socket, FIFO, character-device, and block-device reparse data.

## Key Interfaces
- `ntfs_make_symlink()`
- `ntfs_reparse_tag_dt_types()`
- `ntfs_delete_reparse_index()`
- `ntfs_reparse_set_wsl_symlink()`
- `ntfs_reparse_set_wsl_not_symlink()`

## Important Behavior
Microsoft-tag reparse records are validated as an 8-byte header plus payload; non-Microsoft tags include GUID-sized overhead. WSL symlinks require `IO_REPARSE_TAG_LX_SYMLINK` and a type field of `2`. Non-symlink WSL special files require zero data length and `FILE_ATTRIBUTE_RECALL_ON_OPEN`.

Setting reparse data creates `AT_REPARSE_POINT` if absent, marks `FILE_ATTR_REPARSE_POINT`, updates filename-dirty state, writes the attribute through a fake attribute inode, and inserts an entry into `$Extend/$Reparse:$R`.

Deleting reparse metadata removes the `$R` index entry, clears the inode reparse flag, marks filename metadata dirty, and dirties the MFT record.

## Risks
Reparse data and `$Reparse` index entries must remain synchronized. If index insertion fails after data write, the code attempts to remove the attribute and logs possible corruption if cleanup fails.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/reparse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/reparse.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/reparse.h

## Summary
Declares NTFS reparse-point symbols used by inode, directory, and creation paths.

## Main Contents
- `extern __le16 reparse_index_name[]`
- Symlink target loading and directory-entry type helpers.
- WSL reparse creation helpers.
- Reparse index and reparse data removal helpers.

## Risks
Callers must pair inode flag updates, filename updates, and index/data changes correctly when using these helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/reparse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/runlist.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/runlist.c

## Summary
Implements NTFS runlist storage, merging, mapping-pair decompression/building, VCN-to-LCN lookup, truncation, sparse/compressed-size checks, insertion, hole punching, and range collapse.

## Main Responsibilities
- Reallocate runlist arrays.
- Merge newly decompressed or newly allocated runs into existing runlists.
- Decode NTFS mapping pairs arrays into in-memory `struct runlist_element` arrays.
- Encode runlists back into NTFS mapping pairs arrays.
- Translate VCNs to LCNs with special negative LCN states.
- Find the runlist element containing a VCN.
- Truncate or extend runlists with sparse runs.
- Detect sparse/delalloc runs and calculate compressed allocated size.
- Insert ranges, punch holes, and collapse ranges while preserving or returning removed runs.

## Key Interfaces
- `ntfs_rl_realloc()`
- `ntfs_runlists_merge()`
- `ntfs_mapping_pairs_decompress()`
- `ntfs_rl_vcn_to_lcn()`
- `ntfs_rl_find_vcn_nolock()`
- `ntfs_get_size_for_mapping_pairs()`
- `ntfs_mapping_pairs_build()`
- `ntfs_rl_truncate_nolock()`
- `ntfs_rl_sparse()`
- `ntfs_rl_get_compressed_size()`
- `ntfs_rl_insert_range()`
- `ntfs_rl_punch_hole()`
- `ntfs_rl_collapse_range()`

## Important Behavior
Runlist merging supports append, insert, replace, and split cases when source runs cover unmapped or sparse areas in a destination runlist. Mergeable runs include physically contiguous LCN runs, holes, delayed-allocation runs, and not-mapped runs.

Mapping-pair decompression validates `lowest_vcn`, mapping-pair bounds, run lengths, VCN overflow, LCN deltas, zero-sized data runs, and `highest_vcn`. Base extents may end with `LCN_RL_NOT_MAPPED` to represent later extents or `LCN_ENOENT` as the final terminator.

Mapping-pair building writes compact signed byte encodings for run lengths and LCN deltas, omitting LCN deltas for NTFS 3+ holes. It can return `-ENOSPC` with `stop_vcn`/`stop_rl` populated so callers can continue in another attribute extent.

Hole punching returns a removed runlist through `punch_rl` and replaces the target range with `LCN_HOLE`. Collapse removes a range and renumbers later VCNs.

## Risks
Runlists encode critical physical storage mappings; off-by-one VCN errors or incorrect special-LCN handling can corrupt file data mapping. The functions assume callers hold appropriate runlist locks, and many helpers free input runlists on success.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/runlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/runlist.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/runlist.h

## Summary
Defines NTFS in-memory runlist structures, special LCN values, initialization helper, and runlist/mapping-pair APIs.

## Main Contents
- `struct runlist_element` with `vcn`, `lcn`, and `length`.
- `struct runlist` with element pointer, read/write semaphore, element count, and hint index.
- `ntfs_init_runlist()`.
- Special LCN constants: `LCN_DELALLOC`, `LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`, `LCN_ENOMEM`, `LCN_EIO`, `LCN_EINVAL`.
- Declarations for merge, mapping-pair decompression/building, VCN lookup, truncation, sparse checks, compressed-size accounting, insertion, punching, collapse, and reallocation.

## Important Details
The terminator is represented by an element with `length == 0`; its `lcn` communicates whether the runlist ends normally, is not mapped, or has another special state.

## Risks
Negative LCN constants are semantic values, not ordinary errors in all contexts. Callers must distinguish holes, delayed allocation, not-mapped extents, and true errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/runlist.h -->