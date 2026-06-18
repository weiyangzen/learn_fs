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
