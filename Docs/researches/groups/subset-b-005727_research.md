# subset-b-005727 NTFS Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/mft.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/mft.c

## Purpose
`mft.c` implements the NTFS Master File Table record lifecycle: validating and mapping MFT records, allocating and freeing records, extending `$MFT` and `$MFT/$BITMAP`, applying MST fixups around writes, synchronizing `$MFTMirr`, and providing `$MFT` writeback. It is the persistence core behind inode creation, deletion, extent records, and many metadata mutations.

## Important APIs and Functions
The public entry points are `ntfs_mft_record_check()`, `map_mft_record()`, `unmap_mft_record()`, `map_extent_mft_record()`, `__mark_mft_record_dirty()`, `ntfs_sync_mft_mirror()`, `write_mft_record_nolock()`, `ntfs_mft_record_alloc()`, `ntfs_mft_record_free()`, `ntfs_mft_writepages()`, and `ntfs_mft_mark_dirty()`. Internal helpers include `map_mft_record_folio()`, `ntfs_may_write_mft_record()`, bitmap/data extension helpers, `ntfs_mft_record_layout()`, `ntfs_mft_record_format()`, `lcn_from_index()`, and `ntfs_write_mft_block()`.

## Control Flow and State
Mapping computes the folio index and offset from the record number, reads the `$MFT` mapping, copies the on-disk record into `ni->mrec`, applies `post_read_mst_fixup()`, validates general record fields, then stores the pinned folio and offset in the `ntfs_inode`. Dirty state is per-`ntfs_inode` through `NInoDirty`; `mark_mft_record_dirty()` marks the base VFS inode `I_DIRTY_DATASYNC`.

Allocation first sets the target bit in `$MFT/$BITMAP`, extending bitmap allocation/initialized size if needed, then extends `$MFT/$DATA` allocation and initialized size until the target record exists. It formats records on the way, marks the chosen record in use, prepares base or extent inode state, and updates `vol->mft_data_pos` and free-record counters. Freeing clears `MFT_RECORD_IN_USE`, increments the sequence number, writes the record, then clears the bitmap bit with rollback attempts.

Writeout copies `ni->mrec` back to the folio, applies `pre_write_mst_fixup()`, submits bios per `ni->mft_lcn[]`, optionally updates `$MFTMirr`, and keeps folio references until I/O completion. `$MFT` writeback scans each record in the folio and uses `ntfs_may_write_mft_record()` to avoid racing dirty in-cache inodes, creating/deleting inodes, and extent locks.

## Dependencies and Integration
This file depends heavily on `bitmap`, `lcnalloc`, `attrib`, `inode`, `mst`, `runlist`, folio/page-cache APIs, bios, and VFS writeback. `namei.c` uses allocation/freeing for namespace operations; attribute code uses mapping and dirty marking; runlist mapping feeds physical LCN lookup for writeback.

## Risks
Risk is high. Partial rollback after bitmap, runlist, or mapping-pair updates can leave metadata inconsistent and sets `NVolErrors()`. Lock order is delicate around `$MFT`, extent records, runlist locks, and folio locks. `unmap_mft_record()` decrements references but does not free the copied `mrec` or put the folio in the visible path, so lifetime expectations must be checked elsewhere. `ntfs_sync_mft_mirror()` submits async bio despite documenting synchronous I/O. Any arithmetic mistake in record-to-folio or record-to-LCN conversion risks metadata corruption.

## Test Signals
Exercise create/delete cycles until `$MFT/$BITMAP` and `$MFT/$DATA` extend, record reuse after deletion, extent-record allocation for attribute lists, `$MFTMirr` updates for low records, ENOSPC rollback, writeback during concurrent create/unlink, and corrupted MST/record headers. Kernel tests should watch `NVolErrors`, bitmap/free counters, sequence-number changes, and chkdsk/fsck-style consistency after forced failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/mft.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/mft.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/mft.h

## Purpose
`mft.h` declares the MFT record handling interface used by the NTFS driver and provides small wrappers for dirty marking, extent unmapping, and locked writeout.

## Important APIs and Types
The header exports record mapping (`map_mft_record()`, `map_extent_mft_record()`, `unmap_mft_record()`), dirty marking (`mark_mft_record_dirty()`, `__mark_mft_record_dirty()`), persistence (`write_mft_record()`, `write_mft_record_nolock()`, `ntfs_sync_mft_mirror()`, `ntfs_mft_writepages()`, `ntfs_mft_mark_dirty()`), allocation/free (`ntfs_mft_record_alloc()`, `ntfs_mft_record_free()`), validation (`ntfs_mft_record_check()`), and a declared but not locally implemented `ntfs_mft_records_write()`.

## Control Flow and State
`mark_mft_record_dirty()` atomically tests and sets the `NInoDirty` bit and calls the implementation only on the clean-to-dirty transition. `write_mft_record()` locks the folio stored in `ni->folio`, calls `write_mft_record_nolock()`, and unlocks, serializing explicit MFT writes against page-cache writeback and reads.

## Dependencies and Integration
The header includes `highmem`, `pagemap`, and `inode.h`, and is consumed by inode, attribute, directory, reparse, and MFT implementation code. It exposes the contract that callers must mark mapped records dirty before unmapping after modification.

## Risks
The wrapper assumes `ni->folio` is valid and associated with the mapped `mrec`. The declaration of `ntfs_mft_records_write()` has no implementation in the searched NTFS subtree, which is a build or stale API risk if referenced. Dirty marking is skipped if already dirty, so code that mutates a mapped record must not rely on repeated calls for extra side effects.

## Test Signals
Compile/link tests should catch stale declarations. Runtime tests should confirm `write_mft_record()` is only called for mapped records, lockdep stays clean, and dirty MFT changes reach disk through both explicit write and writeback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/mft.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/mst.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/mst.c

## Purpose
`mst.c` implements NTFS multi-sector transfer protection. It restores sector trailer words after reads, replaces them with an update sequence number before writes, and restores the in-memory record after write submission.

## Important APIs
`post_read_mst_fixup()` validates and deprotects a protected record after disk read. `pre_write_mst_fixup()` increments the update sequence number and writes it into each 512-byte sector trailer while saving original trailers in the update sequence array. `post_write_mst_fixup()` restores original trailers without validation after a successful pre-write step.

## Control Flow and State
The functions use `usa_ofs` and `usa_count` in `struct ntfs_record`. Read fixup treats invalid/missing USA layout as unprotected and returns success, but if any sector trailer does not match the update sequence number it marks the in-memory record magic `BAAD` and returns `-EINVAL`. Pre-write fixup rejects null, `BAAD`, hole, misaligned, or size-inconsistent records, increments USN while skipping `0` and `0xffff`, stores original trailer words into the USA, and overwrites trailers with the USN.

## Dependencies and Integration
MFT mapping uses `post_read_mst_fixup()` before record validation. MFT formatting and write paths use `pre_write_mst_fixup()` before bios. The routines depend on NTFS sector size constants, record magic helpers, endian helpers, and ratelimited logging.

## Risks
The read and write functions intentionally differ: invalid USA layout is success on read but failure on write. Callers must understand that distinction. A wrong `size` or corrupt `usa_count` can silently classify data as unprotected on read. `post_write_mst_fixup()` assumes a prior successful pre-write and performs no bounds validation.

## Test Signals
Tests should include valid records, invalid USA offsets/counts, mismatched trailer words, USN wrap from `0xfffe`, records smaller/larger than 512-byte multiples, and ensuring `BAAD` is only an in-memory error signal after incomplete transfer detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/mst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/namei.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/namei.c

## Purpose
`namei.c` implements NTFS directory inode operations and export support: lookup, create, mkdir, unlink, rmdir, rename, symlink, mknod, hard-link creation, parent lookup, and file-handle decoding. It bridges VFS namespace requests to NTFS Unicode names, file-name attributes, directory indexes, MFT records, security descriptors, EA metadata, and reparse points.

## Important APIs and Functions
The file defines `ntfs_dir_inode_ops` and `ntfs_export_ops`. Core helpers are `ntfs_check_bad_windows_name()`, `ntfs_lookup()`, `ntfs_sd_add_everyone()`, `__ntfs_create()`, `ntfs_delete()`, `__ntfs_link()`, `ntfs_rename()`, and `ntfs_get_parent()`. Public-facing VFS callbacks wrap these helpers: `ntfs_create()`, `ntfs_unlink()`, `ntfs_mkdir()`, `ntfs_rmdir()`, `ntfs_symlink()`, `ntfs_mknod()`, and `ntfs_link()`.

## Control Flow and State
Name handling converts dentry bytes through `ntfs_nlstoucs()` and rejects illegal Windows characters, reserved device names, and optional trailing dot/space cases. Lookup searches directory indexes under `mrec_lock`, handles exact POSIX/WIN32 matches, case-insensitive aliases through `d_add_ci()`, and DOS-name redirection to the corresponding WIN32 name.

`__ntfs_create()` allocates a new VFS inode, initializes NTFS inode state, applies masks/ownership/ACLs, marks parent timestamps, allocates an MFT record, inserts the inode hash as `I_NEW | I_CREATING`, and then under child/parent MFT locks creates standard information, a permissive security descriptor, either index-root or data attributes, WSL reparse data for symlinks/special files, WSL EA metadata, a POSIX `FILE_NAME` attribute, and the parent directory index entry. It sets link count, VFS operations, and instantiates through callers. Error paths remove created attributes, delete reparse index entries, free extent/base MFT records, remove the inode hash, and discard the new inode.

Deletion finds matching `FILE_NAME` attributes by namespace and case rules, checks directory emptiness/hard-link exceptions, removes the directory index entry and attribute, decrements link counts, and when the MFT link count reaches zero marks the inode being deleted and removes reparse/object-id indexes. Rename is implemented as delete target if present, link old inode into the new directory/name, then delete the old name, with rollback by deleting the newly added link if old-name deletion fails.

## Dependencies and Integration
This file integrates with `mft`, `index`, `reparse`, `object_id`, `ea`, ACL, time conversion, Unicode collation, VFS inode/dentry APIs, and NFS export helpers. It marks the NTFS volume dirty before mutating namespace state.

## Risks
Namespace mutation ordering is corruption-sensitive: adding an index entry before an attribute or failing rollback can leave dangling names. Rename is not an atomic metadata transaction. `ntfs_link()` does not call `ntfs_check_bad_windows_name()` unlike create/unlink/mkdir/rename. Several error paths map to `-ENOMEM` for conversion failures even if the underlying error differs. The permissive security descriptor may be policy-sensitive.

## Test Signals
Test exact/case-insensitive/DOS-name lookups, reserved names, hidden dot files, create/mkdir/symlink/mknod with rollback fault injection, hard links across directories, unlink of files with object IDs/reparse points, non-empty directory unlink rules, rename overwrite and cross-directory rename, NFS export parent lookup, and concurrent create/delete writeback interactions involving `I_CREATING` and `NInoBeingDeleted`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/ntfs.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/ntfs.h

## Purpose
`ntfs.h` is a central include for common NTFS constants, conversion macros, inline helpers, external operation tables, global slab caches, and cross-module function declarations.

## Important APIs and Types
The header defines default preallocation and compression constants, byte/cluster/MFT/page/sector conversion macros and inline equivalents, filesystem constants such as `NTFS_BLOCK_SIZE`, `NTFS_SB_MAGIC`, and maximum name/label lengths, case-sensitivity constants, `NTFS_SB()`, `struct option_t`, external operation tables, slab caches, and declarations for compression, superblock flags, MST, Unicode, ioctl, upcase, and block-device I/O functions. It also defines `ntfs_ffs()`.

## Control Flow and State
There is no runtime state machine in this header, but the conversion helpers encode important layout assumptions: cluster size bits/masks, MFT record size bits, page size, and superblock block size drive mapping between logical NTFS objects and Linux page or block addresses.

## Dependencies and Integration
Most NTFS source files include this header to reach `volume.h`, `layout.h`, `inode.h`, logging format, VFS operation exports, and common conversions. MFT, runlist, namei, MST, object-id, quota, and reparse code all depend on declarations or constants here.

## Risks
The macro and inline conversion helpers overlap; drift between them would be dangerous. Several conversions assume bit-shiftable power-of-two sizes configured in `ntfs_volume`. Invalid volume geometry can cascade into wrong folio, cluster, and sector calculations. Central external declarations can hide stale APIs until link time.

## Test Signals
Geometry tests should validate conversions for small and large cluster sizes, MFT records smaller/equal/larger than a page, block sizes different from 512 bytes, and compression cluster constraints. Build tests should catch declaration drift against implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/ntfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/object_id.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/object_id.c

## Purpose
`object_id.c` removes object ID index entries from `$Extend/$ObjId` when an inode with an `AT_OBJECT_ID` attribute is deleted.

## Important APIs and Types
It defines packed index key/data structures matching `$ObjId`, exports `objid_index_name` as `$O`, and provides `ntfs_delete_object_id_index()`. Internal helpers are `open_object_id_index()` and `remove_object_id_index()`.

## Control Flow and State
Opening the index converts `$ObjId` to NTFS Unicode, loads `FILE_Extend`, looks up `$ObjId` by name under the extend directory MFT lock, opens that inode, and obtains an index context for `$O`. Deletion opens the target inode's `AT_OBJECT_ID` attribute, opens the system index, locks the index inode's MFT record, reads the GUID key from the attribute value, looks up the key, removes the matching index entry, marks the index entry and MFT record dirty, and drops all references.

## Dependencies and Integration
Deletion is called from `ntfs_delete()` when the file-name link count reaches zero. It depends on `ntfs_attr_iget()`, Unicode conversion, inode lookup, directory lookup by name, index context management, index lookup/removal, and MFT dirty marking.

## Risks
If `$ObjId` cannot be opened, `ntfs_delete_object_id_index()` silently returns success with no index removal. If the object-id attribute is malformed or short, removal returns `-ENODATA`. Correctness depends on packed struct layout and GUID byte ordering. Failure after attribute removal elsewhere can leave stale `$ObjId` entries.

## Test Signals
Create/delete files with object IDs, missing `$ObjId`, malformed short object-id attributes, absent index entries, and injected index removal failures. Validate that the `$O` entry disappears and that index inode MFT dirtying triggers persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/object_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/object_id.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/object_id.h

## Purpose
`object_id.h` exposes the minimal object-id cleanup interface for NTFS namespace deletion.

## Important APIs
It declares the `$ObjId` index name symbol `objid_index_name[]` and `ntfs_delete_object_id_index(struct ntfs_inode *ni)`.

## Control Flow and State
The header carries no control flow. Its contract is that callers pass the base NTFS inode whose `AT_OBJECT_ID` attribute should be unindexed before final deletion.

## Dependencies and Integration
`namei.c` includes this header and invokes the function when a file's link count reaches zero. Implementation requires `struct ntfs_inode` definitions through including translation units.

## Risks
The header does not include `inode.h`, so it relies on prior declarations in users. The API only covers deletion/unindexing, not creation or update, so callers must not assume full object-id lifecycle support here.

## Test Signals
Build coverage should confirm all users include the necessary NTFS inode declarations. Deletion tests should verify the function is called only for final unlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/object_id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/quota.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/quota.c

## Purpose
`quota.c` marks NTFS quota metadata out of date so Windows can rescan quota entries after Linux-side changes.

## Important API
The only exported function is `ntfs_mark_quotas_out_of_date(struct ntfs_volume *vol)`.

## Control Flow and State
The function exits early if the volume is already marked quota-out-of-date. Otherwise it requires open quota inodes, locks `vol->quota_q_ino`, opens its `I30` index, looks up `QUOTA_DEFAULTS_ID`, validates the entry size and `QUOTA_VERSION`, and checks quota flags. If tracking is enabled/requested or pending deletes exist, it sets `QUOTA_FLAG_OUT_OF_DATE` in the quota defaults entry and marks the index entry dirty. It then sets the in-memory volume flag `NVolSetQuotaOutOfDate()` to avoid repeated attempts.

## Dependencies and Integration
This code depends on quota layout structures from NTFS layout headers, index context APIs, volume flags, inode locking, and NTFS logging. It is intended for volume-level metadata consistency rather than normal VFS quota enforcement.

## Risks
If quota inodes are not open, the function returns false. It does not mark the containing MFT record dirty directly, relying on index dirty handling. Unsupported quota versions, missing defaults entries, or short entries prevent marking and may leave Windows quota state stale.

## Test Signals
Test volumes with quota tracking enabled, disabled, pending deletes, missing quota inodes, missing defaults entry, unsupported versions, and repeated calls after the in-memory out-of-date flag is set. Verify the defaults index entry is dirtied only when flags change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/quota.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/quota.h

## Purpose
`quota.h` declares the NTFS quota out-of-date marker.

## Important API
It includes `volume.h` and declares `bool ntfs_mark_quotas_out_of_date(struct ntfs_volume *vol)`.

## Control Flow and State
There is no internal state in the header. The return contract is boolean success/failure for updating quota metadata or recognizing it is already out of date.

## Dependencies and Integration
Callers need a mounted `ntfs_volume` with quota system inodes available. The implementation uses index and quota layout internals not exposed by this header.

## Risks
The API does not expose detailed error codes, so callers cannot distinguish missing quota inodes, corrupt quota entries, and unsupported versions without logs.

## Test Signals
Compile coverage plus caller tests should verify that false return paths are handled conservatively and do not assume quota metadata was updated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/reparse.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/reparse.c

## Purpose
`reparse.c` handles NTFS reparse point validation, type interpretation, `$Extend/$Reparse` index updates, WSL symlink target extraction, and creation of WSL reparse data for symlinks and special files.

## Important APIs and Types
It defines `reparse_index_name` as `$R`, WSL link payload structure, packed reparse index entry, and exports `ntfs_make_symlink()`, `ntfs_reparse_tag_dt_types()`, `ntfs_delete_reparse_index()`, `ntfs_reparse_set_wsl_symlink()`, and `ntfs_reparse_set_wsl_not_symlink()`. The header also declares `ntfs_remove_ntfs_reparse_data()`, but no implementation appears in this file.

## Control Flow and State
Validation checks total buffer size against `reparse_data_length`, rejects reserved zero tags, accounts for non-Microsoft GUID headers, verifies WSL symlink type `2`, and requires recall-on-open for WSL special-file tags. `ntfs_make_symlink()` reads `AT_REPARSE_POINT`, validates it, maps tags to Unix file types, and for LX symlinks allocates `ni->target` from the stored byte link. Directory-entry type probing opens the inode by MFT reference and maps known tags to `DT_*`.

Index maintenance opens `$Extend/$Reparse` by Unicode lookup, obtains `$R`, and uses `(reparse_tag, file_id)` as key. Setting reparse data creates `AT_REPARSE_POINT` if needed, sets `FILE_ATTR_REPARSE_POINT`, removes old index entries, overwrites the attribute, adds the new index entry, and dirties affected MFT records. Deletion removes the index entry, clears the reparse flag, marks filename dirty, and dirties the inode record.

## Dependencies and Integration
`namei.c` calls WSL setters during symlink and special-file creation and calls deletion during final unlink. The code depends on attribute read/write/add/remove, index APIs, MFT dirtying, Unicode conversion, `$Extend` lookup, and NTFS layout tag definitions.

## Risks
The missing implementation for `ntfs_remove_ntfs_reparse_data()` is a stale declaration/build risk if referenced. If index insertion fails after writing data, the code attempts to remove the attribute but can leave inconsistency. Validation accepts only a subset of tags. `ntfs_reparse_tag_dt_types()` returns `PTR_ERR()` as unsigned int on `ntfs_iget()` failure, which can look like a large directory type value. Some flag handling assigns `ni->flags` rather than ORing in create paths outside this file.

## Test Signals
Test valid/invalid WSL symlink buffers, AF_UNIX/FIFO/CHR/BLK tags, missing `$Reparse`, index add/remove failures, reparse replacement, deletion clearing flags and filename dirty state, directory `DT_*` reporting, and link-target lifetime through `ni->target`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/reparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/reparse.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/reparse.h

## Purpose
`reparse.h` exposes NTFS reparse point operations used by inode setup, namespace deletion, and directory type reporting.

## Important APIs
The header declares `reparse_index_name[]`, `ntfs_make_symlink()`, `ntfs_reparse_tag_dt_types()`, `ntfs_reparse_set_wsl_symlink()`, `ntfs_reparse_set_wsl_not_symlink()`, `ntfs_delete_reparse_index()`, and `ntfs_remove_ntfs_reparse_data()`.

## Control Flow and State
The API separates reading/interpreting reparse data, writing WSL reparse data, and removing index state. Callers are expected to pass NTFS inodes with appropriate MFT/attribute state and to persist dirty records after changes.

## Dependencies and Integration
`namei.c` uses the setters for new symlinks and special files and `ntfs_delete_reparse_index()` during deletion. Directory code can use `ntfs_reparse_tag_dt_types()` for dirent type mapping.

## Risks
`ntfs_remove_ntfs_reparse_data()` is declared but not found in the paired implementation, making it a stale or missing symbol risk. The header relies on externally visible `struct ntfs_inode` and `struct ntfs_volume` declarations.

## Test Signals
Build/link tests should ensure every declaration has an implementation or no references. VFS tests should cover symlink and special-file creation and deletion through this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/reparse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/runlist.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/runlist.c

## Purpose
`runlist.c` implements in-memory NTFS VCN-to-LCN mapping management and mapping-pairs compression/decompression. It is used by non-resident attributes, allocation, sparse/compressed files, MFT extension, hole punching, and range collapse.

## Important APIs and Functions
Public functions include `ntfs_rl_realloc()`, `ntfs_runlists_merge()`, `ntfs_mapping_pairs_decompress()`, `ntfs_rl_vcn_to_lcn()`, `ntfs_rl_find_vcn_nolock()`, `ntfs_get_size_for_mapping_pairs()`, `ntfs_mapping_pairs_build()`, `ntfs_rl_truncate_nolock()`, `ntfs_rl_sparse()`, `ntfs_rl_get_compressed_size()`, `ntfs_rl_insert_range()`, `ntfs_rl_punch_hole()`, and `ntfs_rl_collapse_range()`. Internal helpers handle array movement, mergeability, insertion, append, replace, split, significant-byte encoding, and contiguous-run checks.

## Control Flow and State
Runlists are arrays of `{vcn,lcn,length}` terminated by a zero-length element whose `lcn` is usually `LCN_ENOENT` or `LCN_RL_NOT_MAPPED`. Negative LCN sentinels represent delayed allocation, sparse holes, unmapped regions, no entry, and error states. Merge logic locates where a source runlist fits into a destination runlist and chooses insert, append, replace, or split based on whether it starts/ends at a hole boundary. It preserves or creates unmapped regions and terminators as needed.

Mapping-pairs decompression walks on-disk variable-length pairs, decodes signed VCN lengths and relative LCN deltas, rejects negative lengths, invalid LCNs, overflow, and highest-VCN mismatches, then optionally merges the result into an old runlist. Building mapping pairs performs the inverse, encoding signed minimal-width lengths and LCN deltas, supporting partial ranges and `-ENOSPC` partial success with `stop_vcn` and `stop_rl`.

Truncation shrinks to a terminator or expands with sparse holes. Insert-range splices source runs into a destination at a VCN, splitting destination runs and merging contiguous holes/LCNs. Punch-hole extracts the removed physical runs into `punch_rl` and replaces the range with a hole. Collapse-range extracts a range and shifts following VCNs left.

## Dependencies and Integration
This file depends on NTFS volume geometry, attribute records, overflow helpers, memory allocation, and debug/logging. MFT and attribute allocation use merge/build/decompress to keep non-resident mapping pairs synchronized with in-memory runlists.

## Risks
Runlist correctness is critical: off-by-one VCN updates, terminator mishandling, or failure to merge/split sentinels can corrupt attribute mappings. Caller locking is required but not enforced. Several functions free input runlists on success, so ownership mistakes can cause use-after-free or leaks. Mapping-pair parsing is hardened for overflow, but crafted metadata remains high-risk.

## Test Signals
Unit-style tests should cover every merge shape, unmapped source prefixes, sparse holes, delayed allocation, partial first/last VCN ranges, mapping-pairs round trips, `-ENOSPC` partial builds, truncation shrink/expand, punch-hole and collapse across one or multiple runs, compressed-size accounting, and corrupt mapping-pair inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/runlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/runlist.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/runlist.h

## Purpose
`runlist.h` defines the NTFS in-memory runlist representation and declares runlist manipulation and mapping-pairs APIs.

## Important APIs and Types
`struct runlist_element` maps VCN ranges to LCN ranges. `struct runlist` wraps an array with an `rw_semaphore`, element count, and lookup hint. `ntfs_init_runlist()` initializes empty state. The header defines negative LCN sentinel values: `LCN_DELALLOC`, `LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`, `LCN_ENOMEM`, `LCN_EIO`, and `LCN_EINVAL`. It declares merge, decompress, lookup, build, truncate, sparse, compressed-size, insert-range, punch-hole, collapse-range, and realloc functions.

## Control Flow and State
The state contract is that `runlist->rl` is either null or a sorted, VCN-contiguous array ending in a zero-length terminator. Callers must use the embedded lock to serialize access. `count` tracks allocated/valid elements, while `rl_hint` can cache lookup position for other code.

## Dependencies and Integration
The header includes `volume.h` for volume geometry and exposes functions used by attributes, allocation, compression, MFT extension, and file range operations.

## Risks
Sentinel values are semantically overloaded as negative LCNs and error-like codes. Callers must distinguish holes/unmapped regions from true errors. The API documents no automatic locking; misuse can race runlist mutation. Ownership-transfer semantics of functions that free inputs are only in implementation comments, not visible in prototypes.

## Test Signals
Compile coverage plus focused runlist tests should verify initialization, lock usage by callers, sentinel interpretation, count maintenance, and API behavior for null or malformed runlists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/runlist.h -->
