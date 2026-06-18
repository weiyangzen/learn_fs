# subset-b-005724 Research

This grouped report covers the NTFS attribute, attribute-list, bitmap, collation, compression, block-device I/O, and debug support files in `sources/distributed-fs/ceph-client/fs/ntfs/`. Each section preserves the source path and is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/attrib.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/attrib.c

## Purpose

`attrib.c` is the central NTFS attribute engine. It maps non-resident attribute runlists from on-disk mapping pairs, searches attributes in base and extent MFT records, creates/removes/moves attribute records, converts resident attributes to non-resident and back, resizes attribute data, maintains mapping-pair metadata, and implements allocation-oriented operations such as hole punching, range insertion/collapse, and fallocate-style preallocation.

The file sits between high-level inode/file operations and lower-level NTFS primitives: MFT record mapping/allocation, cluster allocation/freeing, runlist manipulation, attribute-list persistence, page cache I/O, and NTFS metadata dirtying.

## Important APIs, Types, And Functions

- `AT_UNNAMED` is the shared unnamed-attribute sentinel used by callers that need to distinguish unnamed attributes from wildcard-name searches.
- `ntfs_map_runlist_nolock()` maps the runlist fragment containing a VCN while the caller already holds `ni->runlist.lock` for write. It can use a caller-provided `ntfs_attr_search_ctx` or create a temporary one, finds the relevant attribute extent, decompresses mapping pairs, and restores the caller's search context if it had to move across extent records.
- `ntfs_map_runlist()` is the unlocked wrapper that takes the runlist write lock and avoids duplicate work if another thread mapped the VCN first.
- `ntfs_attr_vcn_to_rl()`, `ntfs_attr_vcn_to_lcn_nolock()`, `__ntfs_attr_find_vcn_nolock()`, and `ntfs_attr_find_vcn_nolock()` are the core VCN lookup helpers. They handle mapped, hole, out-of-bounds, and not-yet-mapped states and retry runlist mapping where allowed.
- `ntfs_attr_find()` searches a single MFT record in attribute collation order by type, name, and optional resident value. It validates record boundaries, name bounds, resident value size, and non-resident mapping-pair offsets.
- `ntfs_external_attr_find()` extends lookup through `$ATTRIBUTE_LIST`, maps extent MFT records, validates stale references and instance/type/name agreement, and special-cases enumeration so the attribute-list attribute itself is still returned although it is not listed in its own list.
- `ntfs_attr_lookup()` dispatches to the single-record or attribute-list-aware lookup path and is the public search primitive used throughout the driver.
- `ntfs_attr_get_search_ctx()`, `ntfs_attr_reinit_search_ctx()`, and `ntfs_attr_put_search_ctx()` allocate, reset, and release `struct ntfs_attr_search_ctx`, including MFT record unmapping for base and extent records.
- `ntfs_attr_size_bounds_check()`, `ntfs_attr_can_be_resident()`, and the internal `ntfs_attr_can_be_non_resident()` enforce `$AttrDef` and format constraints before creating or resizing attributes.
- `ntfs_attr_record_resize()` and `ntfs_resident_attr_value_resize()` compact/expand attribute records inside an MFT record with 8-byte alignment.
- `ntfs_attr_make_non_resident()` converts a resident attribute record to non-resident form, allocates clusters, builds mapping pairs, copies the resident value into page cache, updates inode sizes/flags, and rolls back on partial failure.
- `ntfs_attr_set()` writes a byte pattern into page-cache folios for an attribute and marks them dirty.
- `ntfs_attr_set_initialized_size()` updates the first non-resident extent's initialized-size field and in-memory `ni->initialized_size`.
- `ntfs_resident_attr_record_add()` and `ntfs_non_resident_attr_record_add()` create new resident or non-resident attribute records and update `$ATTRIBUTE_LIST` when necessary.
- `ntfs_attr_record_rm()`, `ntfs_attr_rm()`, `ntfs_attr_remove()`, and `ntfs_attr_exist()` remove and query attributes, including freeing clusters and unused extent MFT records.
- `ntfs_attr_add()` chooses a resident or non-resident representation, finds or creates an extent record, creates the record, opens the new attribute when initialization data must be written, and cleans up on failure.
- `ntfs_attr_open()` initializes an open attribute inode from the matching attribute record, derives compression/sparse/encrypted state, duplicates names where needed, and validates compressed attribute constraints.
- `ntfs_attr_close()` releases an open attribute's runlist and dynamically allocated name.
- `ntfs_attr_map_whole_runlist()` walks all extents of a non-resident attribute, mapping every mapping-pair fragment and setting `NInoFullyMapped`.
- `ntfs_attr_record_move_to()` and `ntfs_attr_record_move_away()` move attribute records between base/extent MFT records and update the corresponding attribute-list entry.
- `ntfs_attr_update_mapping_pairs()` rebuilds mapping pairs from the in-memory runlist, splits them across existing or new attribute extents when necessary, updates sparse/compressed size metadata, and removes now-unused extent records.
- `ntfs_attr_expand()`, `ntfs_attr_truncate_i()`, `ntfs_attr_truncate()`, and `__ntfs_attr_truncate_vfs()` route growth/shrink requests to resident or non-resident implementations.
- `ntfs_attr_map_cluster()` allocates physical clusters for a VCN currently represented by a hole or delayed allocation, merges the allocation into the runlist, and either updates mapping pairs immediately or marks the runlist dirty for later.
- `ntfs_attr_readall()` opens and reads a complete small metadata attribute with a 64 KiB general cap and a bitmap-specific cap.
- `ntfs_non_resident_attr_insert_range()`, `ntfs_non_resident_attr_collapse_range()`, and `ntfs_non_resident_attr_punch_hole()` implement runlist range edits for unnamed `$DATA`.
- `ntfs_attr_fallocate()` grows the data stream if needed, optionally restores logical size for keep-size mode, allocates clusters over initialized holes, zeroes newly materialized hole clusters, and flushes dirty mapping pairs at the end.

## Control Flow And Algorithms

Runlist mapping starts from a VCN. If the in-memory runlist has an `LCN_RL_NOT_MAPPED` span, `ntfs_map_runlist_nolock()` locates the attribute extent covering that VCN, calls `ntfs_mapping_pairs_decompress()`, then merges the decoded fragment into `ni->runlist`. Callers that only held a read lock, such as `ntfs_attr_vcn_to_lcn_nolock(..., write_locked=false)`, temporarily upgrade to a write lock and then reacquire the read lock before returning.

Attribute lookup is two-tiered. Inodes without an attribute list use `ntfs_attr_find()` directly against the current MFT record. Inodes with `$ATTRIBUTE_LIST` use `ntfs_external_attr_find()`, which walks sorted list entries, maps the referenced base or extent MFT record, and validates that the attribute record instance, type, name, and VCN range match the list entry. Not-found results intentionally leave the context positioned at the insertion point.

Record creation and resizing use compact MFT-record mutation. `ntfs_make_room_for_attr()` shifts the attribute terminator and following records forward; `ntfs_attr_record_resize()` shifts trailing records backward or forward and updates `bytes_in_use`; add/remove paths then fill or delete the record and mark the affected MFT record dirty.

Resident-to-non-resident conversion is transactional within the limits of metadata mutation. The function allocates clusters, calculates mapping-pair and name offsets, fills a page-cache folio from the resident value if needed, resizes and rewrites the attribute record, builds mapping pairs, updates in-memory state last, and has a rollback path that reconstructs the resident record and frees allocated clusters when possible.

Mapping-pair update is the file's most complex metadata rewrite path. It iterates existing attribute extents in VCN order, updates first-extent sizes and sparse/compressed flags, sizes available mapping-pair space, writes as much of the runlist as fits, marks excess old extents with `NTFS_VCN_DELETE_MARK`, and allocates additional extent MFT records if the runlist no longer fits. After a successful full build, it removes marked obsolete extents.

Resize flow depends on residency. Resident growth first tries to enlarge the value in-place. If it cannot fit, it tries to make the attribute non-resident, then retries as non-resident. If conversion is not possible, it may move other attributes out, add an attribute list, or move the target attribute into a new extent record. Non-resident growth either inserts sparse holes for eligible `$DATA` streams or allocates clusters; shrink frees clusters beyond the new end, truncates the runlist, updates mapping pairs, and may convert zero-size uncompressed attributes back to resident.

Range operations edit the runlist first, then persist metadata. Insert creates a hole run and shifts later VCNs. Collapse removes a range and frees returned physical runs. Punch-hole converts allocated runs into holes and frees detached physical runs after mapping pairs are updated. Fallocate combines truncation, VCN scanning, cluster materialization, direct zeroing for initialized holes, and deferred mapping-pair flush.

## State And Persistence Behavior

The file maintains persistent NTFS state in MFT records, `$ATTRIBUTE_LIST`, mapping pairs, cluster allocation bitmap side effects through allocator/free helpers, and file-name index metadata through `NInoSetFileNameDirty()`. In-memory state includes `ni->runlist.rl/count/rl_hint`, `ni->allocated_size`, `ni->data_size`, `ni->initialized_size`, `ni->itype.compressed.*`, inode flags such as `NInoNonResident`, `NInoSparse`, `NInoCompressed`, `NInoFullyMapped`, and VFS `i_blocks`/`i_size`.

Persistence is explicit. MFT record changes call `mark_mft_record_dirty()`. Attribute-list memory changes are persisted by `ntfs_attrlist_update()`. Mapping-pair changes are written into attribute records by `ntfs_attr_update_mapping_pairs()`. Cluster allocation and freeing are delegated to `lcnalloc` helpers. Some allocation paths intentionally defer mapping-pair persistence by marking `NInoRunlistDirty()` and later flushing when free space is low or fallocate completes.

Locking is central to correctness. Runlist mutation requires `ni->runlist.lock` for write. Size fields are guarded by `ni->size_lock` in paths that race with page-cache operations. Some fallocate and MFT-record paths hold `ni->mrec_lock`. Extent movement uses `base_ni->extent_lock`.

## Dependencies And Integration Points

This file depends on:

- `attrib.h` for public declarations and `struct ntfs_attr_search_ctx`.
- `attrlist.h` for `$ATTRIBUTE_LIST` update/add/remove helpers.
- `lcnalloc.h` for cluster allocation/freeing.
- `mft.h` for MFT record map/unmap/alloc/free and extent record helpers.
- `ntfs.h` for NTFS core types, constants, endian helpers, flags, and logging.
- `iomap.h` and Linux page-cache/iomap/writeback APIs for dirtying pages and zeroing allocated holes.
- Runlist and mapping-pair helpers, including `ntfs_mapping_pairs_decompress()`, `ntfs_mapping_pairs_build()`, `ntfs_runlists_merge()`, `ntfs_rl_*()`, and `ntfs_rl_get_compressed_size()`.

Major integration surfaces include inode open/close through `ntfs_attr_open()` and `ntfs_attr_close()`, data write allocation through `ntfs_attr_map_cluster()`, compression write support through `ntfs_attr_update_mapping_pairs()` and hole punching, metadata readers through `ntfs_attr_readall()`, and VFS truncate/fallocate flows through the resize and fallocate functions.

## Risks And Edge Cases

- Search-context restoration across extent MFT records is fragile. Callers must follow the documented warning that `ctx->mrec` may become `ERR_PTR()` after context restoration failures.
- Several error paths preserve metadata consistency only best-effort. Failures after cluster allocation or partial mapping-pair writes may log leaked clusters or inconsistent metadata requiring chkdsk.
- Attribute-list handling must keep list entries sorted and synchronized with moved or deleted records. A stale sequence number, mismatched instance, or invalid length causes volume error marking.
- Mapping-pair rebuild can recursively force attribute-list creation or record movement. Incorrect free-space calculations can produce `-EAGAIN` retry loops or leave extents marked for deletion.
- Sparse and compressed handling changes record layout by inserting/removing the `compressed_size` field before the name; offset arithmetic must stay aligned and bounds-checked.
- `ntfs_attr_put_search_ctx()` appears to unmap an extent using `ctx->base_ntfs_ino` when `mapped_base_mrec` is true and `ctx->ntfs_ino != ctx->base_ntfs_ino`; this is subtle and should be reviewed against the expected unmap target.
- Some helpers return inconsistent error conventions, such as `ntfs_non_resident_attr_record_add()` returning `-1` on many failures instead of a specific errno.
- Fallocate and cluster mapping can defer mapping-pair persistence; crash consistency depends on later dirty-runlist flush and MFT writeback behavior.
- `ntfs_attr_readall()` caps most attributes at 64 KiB, so callers must not use it for unbounded attribute content.

## Test Signals

Useful tests should exercise: resident attribute growth/shrink and conversion to non-resident; non-resident shrink with cluster freeing; creation/removal of named attributes; attribute-list creation when the base MFT record fills; attribute movement to extent records; lookup enumeration across base and extent records; runlist mapping with multiple extents and holes; mapping-pair rebuild that requires additional extents; sparse growth and de-sparsification; punch-hole/insert/collapse range on unnamed `$DATA`; fallocate keep-size behavior; error handling for corrupt attribute lengths, bad name offsets, stale attribute-list MFT references, and invalid mapping-pair offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/attrib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/attrib.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/attrib.h

## Purpose

`attrib.h` exposes the NTFS attribute subsystem interface. It defines the attribute search context, hole-handling constants, the unnamed-attribute sentinel, inline helpers, and public functions for mapping runlists, searching attributes, resizing, adding/removing attributes, reading whole metadata attributes, and range allocation operations.

## Important APIs, Types, And Functions

- `extern __le16 AT_UNNAMED[]` is the canonical unnamed attribute name.
- `struct ntfs_attr_search_ctx` tracks the currently mapped MFT record, current attribute record, enumeration state, owning inode, attribute-list entry, and base-record state when lookups cross into extent records.
- `enum { HOLES_NO, HOLES_OK }` controls whether resize/growth operations may represent new space as holes.
- Runlist APIs include `ntfs_map_runlist_nolock()`, `ntfs_map_runlist()`, `ntfs_attr_vcn_to_lcn_nolock()`, `ntfs_attr_find_vcn_nolock()`, `__ntfs_attr_find_vcn_nolock()`, `ntfs_attr_map_whole_runlist()`, and `ntfs_attr_vcn_to_rl()`.
- Search and attribute-list APIs include `ntfs_attr_lookup()`, `load_attribute_list()`, `ntfs_attr_get_search_ctx()`, `ntfs_attr_reinit_search_ctx()`, and `ntfs_attr_put_search_ctx()`.
- Mutation APIs include `ntfs_attr_record_resize()`, `ntfs_resident_attr_value_resize()`, `ntfs_attr_make_non_resident()`, `ntfs_attr_set()`, `ntfs_attr_set_initialized_size()`, `ntfs_attr_add()`, `ntfs_attr_record_rm()`, `ntfs_attr_record_move_to()`, `ntfs_attr_record_move_away()`, `ntfs_attr_update_mapping_pairs()`, `ntfs_attr_rm()`, `ntfs_attr_remove()`, and `ntfs_attr_fallocate()`.
- Size and capability helpers include `ntfs_attr_size()`, `ntfs_attr_size_bounds_check()`, and `ntfs_attr_can_be_resident()`.
- `ntfs_attrs_walk()` is inline syntactic sugar for enumerating all attributes using `ntfs_attr_lookup(AT_UNUSED, ...)`.

## Control Flow And Usage

Callers typically obtain a `struct ntfs_attr_search_ctx` with `ntfs_attr_get_search_ctx()`, call `ntfs_attr_lookup()` repeatedly or through `ntfs_attrs_walk()`, use `ctx->attr` and `ctx->mrec`, then release the context with `ntfs_attr_put_search_ctx()`. When an operation changes the lookup target, `ntfs_attr_reinit_search_ctx()` resets enumeration to the beginning.

Runlist callers either use the unlocked wrapper `ntfs_map_runlist()` or call `_nolock` variants while holding the correct runlist lock. Mutating APIs assume the caller understands whether the target `ntfs_inode` is a base inode or an attribute inode.

## State And Persistence Behavior

The header itself has no persistence, but its API contract exposes persistent state changes in MFT records, mapping pairs, attribute lists, runlists, cluster allocation, and inode size/flag fields. `struct ntfs_attr_search_ctx` may hold mapped MFT records and extent inode references, so lifecycle correctness directly affects mapped-record persistence and memory safety.

## Dependencies And Integration Points

The header includes `ntfs.h` and `dir.h`, so it integrates with core NTFS types, constants, VFS inode wrapping, and name collation support. It is consumed by attribute-list handling, compression, inode operations, bitmap management, and any code that needs to locate or mutate NTFS attributes.

## Risks And Edge Cases

- Search contexts carry mapped-record ownership. Forgetting `ntfs_attr_put_search_ctx()` leaks mappings; reusing a context after a documented mapping failure can dereference invalid pointers.
- `ntfs_attr_size()` returns resident value length or non-resident data size only; it does not return allocated size or initialized size.
- `ntfs_attrs_walk()` reports `-1` on error with errno in comments inherited from older code, while the underlying kernel code returns negative errno values; users should verify actual call-site expectations.
- Many APIs require specific lock state that is documented in implementation comments rather than encoded in types.

## Test Signals

Compile-time coverage should verify all declarations match implementations. Runtime tests should cover search-context enumeration, reinitialization after extent lookups, runlist lookup wrappers under read/write lock modes, and all public mutation APIs through higher-level inode operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/attrib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/attrlist.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/attrlist.c

## Purpose

`attrlist.c` manages the `$ATTRIBUTE_LIST` attribute for NTFS inodes whose attributes span multiple MFT records. It determines whether an attribute list is still needed, persists the in-memory list to its attribute stream, and adds/removes list entries when attribute records are created, moved, or deleted.

## Important APIs, Types, And Functions

- `ntfs_attrlist_need()` walks `ni->attr_list` and returns whether any list entry points to an MFT record other than the base inode. It returns `1` when an extent record is referenced, `0` when all entries are local, and negative errno on invalid state.
- `ntfs_attrlist_update()` opens the unnamed `AT_ATTRIBUTE_LIST` attribute inode, truncates it to `base_ni->attr_list_size`, writes the in-memory `base_ni->attr_list` bytes, updates non-resident attribute-list state, marks the base list dirty, and drops the attribute inode.
- `ntfs_attrlist_entry_add()` builds a new sorted `struct attr_list_entry` for an attribute record, inserts it into a newly allocated copy of the list, swaps it into the base inode, persists it, and frees the old list on success.
- `ntfs_attrlist_entry_rm()` removes `ctx->al_entry` from the base inode's list by copying all other entries into a new buffer and then persists the result.

## Control Flow And Algorithms

Adding an entry first maps the MFT record containing the attribute to capture a correct MFT reference and sequence number. If the caller passed an extent inode, the function switches to the base inode. It locates the insertion position with `ntfs_attr_lookup()` using the target type, name, lowest VCN, and resident value ordering, then constructs an aligned list entry with type, name, `lowest_vcn`, `mft_reference`, and instance. The list is replaced only after the new buffer is complete; on persistence failure the old pointer and size are restored.

Updating the on-disk list is done through normal attribute I/O rather than by direct MFT manipulation. It truncates the attribute stream, handles a special recovery case for `$MFT` where an `-ENOSPC` truncate tries to reset and retry, writes the entire list with `ntfs_inode_attr_pwrite()`, and marks the in-memory state dirty.

Removal computes the new length, allocates a replacement buffer, copies the prefix and suffix around the removed entry, swaps it into `base_ni`, and calls `ntfs_attrlist_update()`.

## State And Persistence Behavior

The primary state is `base_ni->attr_list`, `base_ni->attr_list_size`, `NInoAttrList`, `NInoAttrListNonResident`, and `NInoAttrListDirty`. Persistence happens by resizing and writing the `AT_ATTRIBUTE_LIST` attribute stream. Entry add is rollback-aware for the in-memory pointer/size if persistence fails; entry remove swaps the in-memory list before update and does not restore it if the update fails.

## Dependencies And Integration Points

The file includes `mft.h`, `attrib.h`, and `attrlist.h`. It relies on `ntfs_attr_iget()`, `ntfs_attr_truncate_i()`, `ntfs_attr_truncate()`, `i_size_write()`, `ntfs_inode_attr_pwrite()`, MFT map/unmap helpers, `ntfs_attr_get_search_ctx()`, and `ntfs_attr_lookup()`. It is called from `attrib.c` when records are added, removed, moved, or when mapping-pair updates need list metadata refreshed.

## Risks And Edge Cases

- `ntfs_attrlist_need()` trusts list entry lengths enough to advance; corrupt zero-length entries would be dangerous if validation has not already happened.
- `ntfs_attrlist_entry_add()` uses `attr->data.non_resident.lowest_vcn` in a duplicate check even in the branch after lookup succeeds; resident attributes rely on earlier lookup parameters to avoid misuse.
- Removal does not roll back `base_ni->attr_list` if `ntfs_attrlist_update()` fails, so in-memory and on-disk state can diverge until higher-level error handling reacts.
- Attribute-list updates can recurse into attribute resizing and allocation paths, so lock ordering and ENOSPC behavior are sensitive.

## Test Signals

Tests should create enough attributes to force `$ATTRIBUTE_LIST`, add records in sorted and unsorted type/name/VCN order, move records to extent MFT records, remove entries until the list is no longer needed, verify non-resident list updates, and inject write/truncate failures to check rollback and error reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/attrlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/attrlist.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/attrlist.h

## Purpose

`attrlist.h` declares the small public interface for NTFS `$ATTRIBUTE_LIST` management.

## Important APIs, Types, And Functions

- `ntfs_attrlist_need(struct ntfs_inode *ni)` checks whether an inode still requires an attribute list.
- `ntfs_attrlist_entry_add(struct ntfs_inode *ni, struct attr_record *attr)` inserts a new list entry for an attribute record.
- `ntfs_attrlist_entry_rm(struct ntfs_attr_search_ctx *ctx)` removes the current list entry from the base inode.
- `ntfs_attrlist_update(struct ntfs_inode *base_ni)` persists the in-memory attribute-list bytes to the `$ATTRIBUTE_LIST` stream.

## Control Flow And Usage

Callers in the attribute engine invoke these helpers after creating, moving, deleting, or resizing attribute records. The header includes `attrib.h` because removal uses `struct ntfs_attr_search_ctx` and add uses `struct attr_record`/`struct ntfs_inode` from the NTFS attribute model.

## State And Persistence Behavior

The declared functions mutate `base_ni->attr_list` and persist `AT_ATTRIBUTE_LIST`. This header does not own state, but its APIs are part of the transaction boundary for MFT record changes that affect attribute-list entries.

## Dependencies And Integration Points

The header is consumed by `attrib.c` and implemented by `attrlist.c`. It is tied to MFT record layout, attribute search context lifecycle, and inode flags that indicate whether an attribute list exists or is non-resident.

## Risks And Edge Cases

The interface does not encode whether `ni` is a base or extent inode; implementations normalize in some paths. Callers must ensure the supplied search context still points at the entry to remove and has not been invalidated by a relookup or record movement.

## Test Signals

Build coverage should ensure prototypes stay aligned with implementation. Runtime coverage comes from attribute add/remove/move tests that validate correct `$ATTRIBUTE_LIST` bytes and persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/attrlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/bdev-io.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/bdev-io.c

## Purpose

`bdev-io.c` provides NTFS-specific helpers for direct block-device reads and page-cache-mediated block-device writes. It is used where metadata code needs to access raw device bytes outside ordinary file data paths.

## Important APIs, Types, And Functions

- `ntfs_bdev_read(struct block_device *bdev, char *data, loff_t start, size_t size)` synchronously reads bytes from a sector-aligned device offset. Non-vmalloc buffers use `bdev_rw_virt()`; vmalloc buffers are filled through one or more BIOs with `REQ_META | REQ_SYNC`.
- `ntfs_bdev_write(struct super_block *sb, void *buf, loff_t start, size_t size)` updates `sb->s_bdev->bd_mapping` folios covering the target range, copies bytes into the page cache, marks folios uptodate and dirty, and returns immediately after dirtying.

## Control Flow And Algorithms

The read path validates 512-byte sector alignment, chooses a simple virtual-buffer helper for linear memory, or builds a BIO chain for vmalloc-backed memory. It repeatedly adds vmalloc chunks to the current BIO; if the BIO fills, it chains a new BIO, submits the previous one, and continues. The last BIO is submitted with `submit_bio_wait()`.

The write path computes page indices from byte offsets, reads each block-device mapping folio, copies the corresponding slice from `buf`, and dirties the folio. It handles partial first/last pages through `from`, `to`, and `buf_off` offsets.

## State And Persistence Behavior

Reads do not modify persistent state. Writes modify the block device address-space page cache and rely on normal dirty-page writeback for persistence. `ntfs_bdev_read()` invalidates vmalloc mappings only if `op == REQ_OP_READ`, but `op` includes flags, so this condition is false as written for `REQ_OP_READ | REQ_META | REQ_SYNC`.

## Dependencies And Integration Points

The file depends on Linux block-layer APIs (`bio_alloc`, `bio_add_vmalloc_chunk`, `bio_chain`, `submit_bio`, `submit_bio_wait`, `bdev_rw_virt`) and folio/page-cache APIs for block-device mapping writes. It includes `ntfs.h` for `ntfs_error()` logging and NTFS constants.

## Risks And Edge Cases

- `bio_alloc()` return values are not checked for NULL; allocation failure can lead to dereference faults.
- The vmalloc read path chains and submits prior BIOs but only waits on the last BIO, relying on `bio_chain()` completion semantics; this should be validated for the target kernel version.
- The invalidation check compares `op` to `REQ_OP_READ` after OR-ing flags, so the vmalloc destination range may not be invalidated as intended.
- `ntfs_bdev_write()` calls `memcpy_to_folio(folio, from, buf + buf_off, to)` with `to` as a length-like value, but `to` is calculated as an end offset within the page. For nonzero `from`, this can copy too much unless the API expects an end offset, which should be verified.
- Writes are not synchronous and do not report later writeback errors.

## Test Signals

Tests should cover sector misalignment rejection, non-vmalloc read, vmalloc read spanning more BIO segments than one BIO can hold, partial first/last page writes, block-device read folio failure, and writeback/invalidation behavior under metadata consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/bdev-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/bitmap.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/bitmap.c

## Purpose

`bitmap.c` implements NTFS bitmap operations for cluster trimming and setting or clearing ranges of bits in bitmap attributes. It is used for volume free-space discard and metadata bitmap mutation.

## Important APIs, Types, And Functions

- `ntfs_trim_fs(struct ntfs_volume *vol, struct fstrim_range *range)` scans the volume cluster bitmap for zero bits, aligns free ranges to the block device discard granularity, issues discard requests, and returns the total trimmed byte count in `range->len`.
- `__ntfs_bitmap_set_bits_in_run(struct inode *vi, s64 start_bit, s64 count, u8 value, bool is_rollback)` sets or clears a bitmap bit range across one or more folios and rolls back already modified bits if a later folio cannot be mapped.

## Control Flow And Algorithms

Trim converts byte start/length into cluster bounds, allocates a file readahead state, reads cluster-bitmap folios, and interprets each page as an `unsigned long` bitset. It uses `find_next_zero_bit()` to locate free runs and `find_next_bit()` to find their end. Each run is converted back to bytes, aligned to discard granularity, checked against `range->minlen`, and discarded with `blkdev_issue_discard()`.

Bitmap mutation computes the first and last folio indices containing the range, maps the first folio, handles a partial first byte bit-by-bit, fills full bytes with `memset()`, advances through intermediate folios, and handles a partial final byte. Each folio is marked dirty and unlocked. If a subsequent folio read fails, the function recursively calls itself in rollback mode to invert the already modified prefix.

## State And Persistence Behavior

Bitmap changes are made in the target bitmap inode's page cache and marked dirty for writeback. When mutating the volume `$Bitmap` (`FILE_Bitmap`), it also calls `ntfs_set_lcn_empty_bits()` to update auxiliary free-space accounting for the affected bits. Trim does not change NTFS metadata; it informs the block device that free clusters can be discarded.

## Dependencies And Integration Points

The file depends on Linux bit operations, block discard APIs, folio mapping, and NTFS helpers such as `ntfs_bytes_to_cluster()`, `ntfs_cluster_to_bytes()`, `ntfs_get_locked_folio()`, and `ntfs_set_lcn_empty_bits()`. The inline public wrappers live in `bitmap.h`.

## Risks And Edge Cases

- `__ntfs_bitmap_set_bits_in_run()` does not explicitly special-case `count == 0`; `end_index = (start_bit + cnt - 1) >> ...` underflows for zero count.
- The rollback path can itself fail, in which case the volume is marked erroneous and metadata may remain inconsistent.
- The calls to `ntfs_set_lcn_empty_bits()` for partial first/final bytes pass a count but not an intra-byte start offset; this depends on that helper's interpretation of page/index state and should be reviewed.
- Trim's alignment can reduce a valid free cluster run to zero discarded bytes; this is intended, but tests need to cover `range->minlen` and discard granularity interactions.
- The bitmap folio is interpreted as `unsigned long *`, so bit order and machine word assumptions must match NTFS's on-disk little-endian bitmap semantics on supported architectures.

## Test Signals

Tests should set and clear bit ranges starting and ending at unaligned bits, crossing page boundaries, and spanning many pages; inject a later-page read failure to validate rollback; check `$Bitmap` free-space accounting updates; exercise fstrim over empty, full, and fragmented bitmaps; and validate discard range alignment and `range->len` reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/bitmap.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/bitmap.h

## Purpose

`bitmap.h` declares NTFS bitmap operations and provides inline convenience wrappers for setting or clearing bitmap ranges and individual bits.

## Important APIs, Types, And Functions

- `ntfs_trim_fs()` exposes filesystem discard over free clusters.
- `__ntfs_bitmap_set_bits_in_run()` is the implementation entry point that also supports internal rollback mode.
- `ntfs_bitmap_set_bits_in_run()` calls the implementation with rollback disabled.
- `ntfs_bitmap_set_run()` and `ntfs_bitmap_clear_run()` set or clear a range.
- `ntfs_bitmap_set_bit()` and `ntfs_bitmap_clear_bit()` mutate a single bit.

## Control Flow And Usage

Callers use the inline wrappers for ordinary bitmap changes and never pass rollback mode directly. Range helpers are thin enough that all validation and folio mutation happen in `bitmap.c`.

## State And Persistence Behavior

The header has no state. The declared operations mutate bitmap inode page cache and, for the volume bitmap, associated free-space state. Persistence is through dirty folio writeback.

## Dependencies And Integration Points

It includes Linux `fs.h` for `struct inode` and `volume.h` for `struct ntfs_volume`. It is used by allocation/freeing paths and fstrim support.

## Risks And Edge Cases

The inline wrappers do not validate count or bit positions; callers must rely on the implementation's validation. Single-bit helpers pass `count = 1`, avoiding the zero-count underflow risk in the implementation.

## Test Signals

Build tests should verify wrapper declarations match the implementation. Functional coverage should be driven through allocator paths, direct bitmap range mutation tests, and fstrim tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/collate.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/collate.c

## Purpose

`collate.c` implements NTFS index collation rules used to order keys in NTFS indexes. It supports binary comparisons, filename collation, single little-endian ULONG comparison, and arrays of little-endian ULONGs.

## Important APIs, Types, And Functions

- `ntfs_collate_binary()` compares byte strings lexicographically and then by length.
- `ntfs_collate_ntofs_ulong()` compares two 4-byte little-endian integers and rejects non-4-byte inputs.
- `ntfs_collate_ntofs_ulongs()` compares arrays of little-endian 32-bit integers and expects equal lengths aligned to 4 bytes.
- `ntfs_collate_file_name()` compares filename attributes first case-insensitively using the volume upcase table and then case-sensitively as a tiebreaker.
- `ntfs_collate()` dispatches based on the on-disk collation rule and returns ordering or `-EINVAL` for unknown/invalid rules.

## Control Flow And Algorithms

The public dispatcher switches on the CPU-converted collation rule. Binary collation is a `memcmp()` over the shorter input plus length comparison. Filename collation delegates to `ntfs_file_compare_values()` twice. ULONG-array collation loops element by element until a difference is found and then returns `cmp_int()`.

## State And Persistence Behavior

The file is pure comparison logic and does not persist state. It reads the volume upcase table for filename ordering and logs errors for unsupported or invalid rules.

## Dependencies And Integration Points

It includes `collate.h`, `debug.h`, `ntfs.h`, and Linux `sort.h` for `cmp_int()`. It integrates with index and directory code that needs to compare NTFS index keys according to the rule stored in an index root.

## Risks And Edge Cases

- `ntfs_collate_ntofs_ulongs()` returns `-1` on invalid length after logging, which is also a valid less-than ordering. That can conflate malformed input with ordering unless callers validate lengths earlier.
- `ntfs_collate_ntofs_ulong()` uses `-EINVAL`, whereas the array variant uses `-1`, so error signaling is inconsistent.
- The switch cases call `le32_to_cpu()` on constants, which assumes the collation constants are typed as little-endian values; this is consistent with the surrounding NTFS style but should stay aligned with definitions.

## Test Signals

Tests should cover binary prefix ordering, filename case-insensitive equality with case-sensitive tiebreak, invalid ULONG lengths, ULONG-array ordering and malformed lengths, and dispatcher behavior for unsupported collation rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/collate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/collate.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/collate.h

## Purpose

`collate.h` declares NTFS collation support and provides a fast inline check for supported collation rules.

## Important APIs, Types, And Functions

- `ntfs_is_collation_rule_supported(__le32 cr)` returns true for the implemented binary, filename, single ULONG, and ULONG-array rules, after checking the numeric rule range.
- `ntfs_collate()` compares two values using a selected collation rule.

## Control Flow And Usage

Index setup or validation code can call `ntfs_is_collation_rule_supported()` before accepting an index root's rule. Comparison call sites pass the volume, rule, two data pointers, and their byte lengths to `ntfs_collate()`.

## State And Persistence Behavior

The header owns no state and performs no persistence. It gates which on-disk index collation rules the driver is willing to process.

## Dependencies And Integration Points

It includes `volume.h` because comparisons require `struct ntfs_volume`, especially for filename collation through the upcase table.

## Risks And Edge Cases

The support predicate is easy to misread because of mixed `unlikely()` and `&&`/`||` precedence, but semantically it rejects rules outside the four implemented values and their expected numeric ranges. Any new collation implementation must update both the predicate and dispatcher.

## Test Signals

Tests should check support detection for each implemented constant, nearby unsupported values in the `0x00..0x02` and `0x10..0x13` ranges, and completely unknown rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/collate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/compress.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/compress.c

## Purpose

`compress.c` implements NTFS compressed attribute read and write support. It owns a shared decompression buffer, decodes NTFS compression blocks into page-cache pages, compresses 4 KiB sub-blocks with an LZ77-style encoder, writes compressed blocks to newly allocated clusters, and exposes a compressed write path for unnamed data streams.

## Important APIs, Types, And Functions

- `allocate_compression_buffers()` and `free_compression_buffers()` manage the global `ntfs_compression_buffer`.
- `zero_partial_compressed_page()` and `handle_bounds_compressed_page()` zero regions beyond initialized size during compressed reads.
- `ntfs_decompress()` parses NTFS compressed sub-block headers, symbol tokens, and phrase tokens, writing decompressed bytes into an array of destination pages and finalizing completed pages.
- `ntfs_read_compressed_block(struct folio *folio)` loads all pages overlapping the compression block(s) that contain the requested folio, reads the compressed clusters from the block device, distinguishes sparse/uncompressed/compressed compression blocks, and fills page-cache pages.
- `struct compress_context`, `ntfs_hash()`, `ntfs_best_match()`, and `ntfs_skip_position()` implement hash-chain match finding for compression.
- `ntfs_compress_block()` compresses one 4 KiB NTFS sub-block or emits an uncompressed sub-block if compression is ineffective.
- `ntfs_write_cb()` compresses a whole compression block, decides whether to store compressed, sparse/all-zero, or uncompressed data, punches the old block, allocates new clusters, updates runlist and mapping pairs, and writes data through BIOs.
- `ntfs_compress_write()` is the public compressed write path. It expands the attribute if needed, reads/locks all pages in each affected compression block, copies user data into those pages, calls `ntfs_write_cb()`, and releases pages.

## Control Flow And Algorithms

Compressed reads start by aligning the requested page index to compression-block boundaries, calculating the target page within the block, and grabbing all destination pages that are not dirty or already uptodate. For each compression block, the code locks the global compression buffer, reads physical clusters through the attribute runlist and the block device mapping, then chooses a decode path. A fully sparse block zeroes destination pages. A block with all clusters present and no sparse break is copied as uncompressed. Otherwise `ntfs_decompress()` decodes sub-block headers and LZ phrase tokens.

`ntfs_decompress()` operates while holding `ntfs_cb_lock`. It validates sub-block boundaries, handles uncompressed sub-blocks by copying 4096 bytes, and handles compressed sub-blocks by reading tag bytes. A zero tag bit copies a literal; a one tag bit reads a 16-bit phrase token, derives backward offset and length from the current destination offset, and copies possibly overlapping data. Page finalization is staged so the lock is dropped before page unlock/put operations.

Compression writes operate per compression block. `ntfs_compress_write()` ensures the stream is large enough, then for each affected compression block reads all block pages, copies from the iov iterator into the relevant page offsets, and calls `ntfs_write_cb()`. `ntfs_write_cb()` vmaps source pages, allocates temporary destination pages, compresses each 4 KiB sub-block, detects all-zero compressed output, appends a terminator for compressed blocks, rounds to cluster size, or falls back to uncompressed data. It then punches the old compression-block range, allocates clusters for the new representation, merges the allocation into the runlist, updates mapping pairs, and writes pages via BIO.

The compressor uses a hash table of 3-byte sequences, a bounded search depth, lazy parsing, and a "nice match" early stop. It emits NTFS phrase tokens whose offset/length bit split changes as the current sub-block offset grows.

## State And Persistence Behavior

Global state is `ntfs_compression_buffer`, protected by `ntfs_cb_lock`. Read state is the page cache: pages are kmap'ed, filled, marked uptodate, unlocked, and put. Write state changes both data and metadata: old cluster ranges are punched to holes, new clusters are allocated, `ni->runlist` is merged, mapping pairs are persisted with `ntfs_attr_update_mapping_pairs()`, BIO writes send compressed/uncompressed bytes to disk, and `NInoSetFileNameDirty()` plus `mark_mft_record_dirty()` mark metadata for writeback.

Sparse all-zero compression blocks are represented by punching the old block and allocating no new clusters. Compressed and sparse size accounting is delegated to mapping-pair update and attribute metadata helpers.

## Dependencies And Integration Points

The file depends on Linux fs, block, vmalloc, slab, page-cache, BIO, and iov-iterator APIs. NTFS dependencies include `attrib.h` for runlist mapping, hole punching, expansion, and mapping-pair updates; `inode.h` for inode access; `lcnalloc.h` for cluster allocation; `mft.h` for dirtying MFT records; and core NTFS conversion/logging helpers.

It integrates with the read-folio path for compressed unnamed `$DATA`, compressed write operations, cluster allocation/freeing, block-device mapping reads, and the attribute engine's mapping-pair persistence.

## Risks And Edge Cases

- The global compression buffer serializes all compressed reads and parts of read decoding, limiting concurrency.
- `ntfs_decompress()` assumes `PAGE_SIZE >= 4096` and depends on callers having mapped destination pages with `kmap_local_page()`.
- Several BIO allocation and page allocation paths have limited recovery. `bio_alloc()` is not always checked before use.
- `ntfs_compress_block()` documents returning `0` on error but returns `-ENOMEM` through an unsigned return type when context allocation fails; callers treat nonzero as a size, which can mis-handle allocation failure.
- `ntfs_write_cb()` calls `vunmap(outbuf)` even when `outbuf` allocation failed and can call `submit_bio_wait(bio)` with `bio == NULL` if no data was added, depending on path.
- The compressed write path clears dirty/uptodate only for `i < ip`, where `ip` tracks the last copied page and may not cover every modified page in edge cases.
- Read classification of "uncompressed compression block" depends on whether all clusters in the compression unit are physically present; malformed compressed data and mixed sparse/allocated layouts must be handled carefully.
- Error paths after punching old clusters but before successful write can lose data or leave metadata inconsistent.

## Test Signals

Tests should cover compressed reads of sparse blocks, uncompressed blocks, valid compressed blocks with literals and overlapping phrase tokens, corrupted sub-block headers, EOF inside a compression block, initialized-size zeroing, dirty destination pages that must not be overwritten, writes that compress well, writes that fall back to uncompressed, all-zero writes that become sparse, partial-block writes, expansion before compressed write, ENOSPC or BIO failure after punching, and concurrent compressed reads to validate buffer locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/debug.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/debug.c

## Purpose

`debug.c` centralizes NTFS warning, error, and optional debug logging. It formats messages with function names and device identifiers, rate-limits warnings/errors in non-debug builds, invokes filesystem error handling for errors tied to a superblock, and can dump runlists when compiled with `DEBUG`.

## Important APIs, Types, And Functions

- `__ntfs_warning()` formats a warning message using `struct va_format` and emits it through `pr_warn()` or `pr_warn_ratelimited()`.
- `__ntfs_error()` formats an error message through `pr_err()` or `pr_err_ratelimited()` and calls `ntfs_handle_error(sb)` when a superblock is supplied.
- `debug_msgs` is a runtime flag, present only under `DEBUG`, that gates debug messages.
- `__ntfs_debug()` emits debug messages with file, line, and function context when `debug_msgs` is enabled.
- `ntfs_debug_dump_runlist()` prints each runlist element, including special negative LCN states, in debug builds.

## Control Flow And Algorithms

Warning and error functions calculate whether the function name is non-empty, bind varargs to `va_format`, and select device-specific or generic log format based on whether `sb` is non-NULL. Debug builds use non-rate-limited logging; non-debug builds rate-limit warnings and errors. Error logging additionally routes the superblock to `ntfs_handle_error()`.

Runlist dumping iterates until a zero-length terminator, maps negative LCN sentinels to readable labels, and prints VCN, LCN/sentinel, and run length.

## State And Persistence Behavior

The file does not persist NTFS metadata directly. Its only state is `debug_msgs` under `DEBUG`. `__ntfs_error()` can indirectly change filesystem state through `ntfs_handle_error(sb)`, which may mark the volume or mount state according to broader NTFS policy.

## Dependencies And Integration Points

It includes `debug.h`, which includes Linux `fs.h` and `runlist.h`. The functions are called throughout the NTFS driver via macros in `debug.h`, so they are the standard reporting path for corruption, I/O failure, and diagnostic output.

## Risks And Edge Cases

- Passing `NULL` as the superblock avoids `ntfs_handle_error()`, so callers must choose intentionally for corruption that should mark the volume erroneous.
- In non-debug builds, warning/error rate limiting can suppress repeated signals during severe metadata corruption.
- `ntfs_debug_dump_runlist()` assumes the runlist is terminated and caller-provided synchronization protects it; corrupt or concurrently modified runlists can produce invalid reads.

## Test Signals

Tests should verify formatted output paths with and without superblocks, rate-limited vs debug build behavior, `ntfs_handle_error()` invocation for errors, debug message gating by `debug_msgs`, and runlist dump formatting for normal runs, holes, delayed allocation, not-mapped, and terminator entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/debug.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/debug.h

## Purpose

`debug.h` declares and wraps NTFS logging helpers. It provides compile-time debug/no-debug behavior while preserving printf-style checking for warning and error functions.

## Important APIs, Types, And Functions

- Under `DEBUG`, `debug_msgs`, `__ntfs_debug()`, `ntfs_debug()`, and `ntfs_debug_dump_runlist()` are active.
- Without `DEBUG`, `ntfs_debug()` and `ntfs_debug_dump_runlist()` compile to no-op blocks that still type-check arguments through unreachable references.
- `__ntfs_warning()` and the `ntfs_warning()` macro emit warnings with caller function context.
- `__ntfs_error()` and the `ntfs_error()` macro emit errors with caller function context.
- `ntfs_handle_error(struct super_block *sb)` is declared as the error-policy hook called by `__ntfs_error()`.

## Control Flow And Usage

Call sites use `ntfs_debug()`, `ntfs_warning()`, and `ntfs_error()` rather than the underscored functions. The macros automatically pass `__func__`, and debug builds also pass `__FILE__` and `__LINE__`.

## State And Persistence Behavior

The header itself has no persistent state. Its macros influence whether debug messages are emitted and whether error calls can trigger the implementation's filesystem error handler.

## Dependencies And Integration Points

It includes Linux `fs.h` for `struct super_block` and `runlist.h` for debug runlist dumping. It is included by most NTFS implementation files and is part of the driver's common diagnostics interface.

## Risks And Edge Cases

- No-op debug macros avoid evaluating runtime logging calls, so side effects must never be embedded in debug arguments.
- Warning/error macros always pass `__func__`; callers that need no function prefix must call underscored functions directly, which is uncommon.
- The declaration of `ntfs_handle_error()` makes logging part of error-state policy, so using `ntfs_error()` for benign messages can have side effects.

## Test Signals

Build tests should cover DEBUG and non-DEBUG configurations, printf-format checking, no-op macro type checking, and linkage of `ntfs_handle_error()`. Runtime tests should verify warning/error paths through `debug.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/debug.h -->
