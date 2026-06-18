# Group Research: group_800_linux_sources_os_linux_linux_fs_ntfs_attrib_c_sources_os_linux_linux_010e76a434d6

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/attrib.c -->
# File Research: sources/os/linux/linux/fs/ntfs/attrib.c

Implements the Linux NTFS driver's core attribute engine: attribute lookup, attribute-list traversal, resident/non-resident conversion, runlist mapping, mapping-pairs rewrite, attribute insertion/removal, truncation/expansion, cluster mapping, hole punching, range insert/collapse, and fallocate support.

Key entry points:
- `ntfs_map_runlist_nolock()` / `ntfs_map_runlist()` map compressed on-disk mapping pairs into `ni->runlist`, preserving caller search-context state when provided.
- `ntfs_attr_vcn_to_lcn_nolock()`, `ntfs_attr_find_vcn_nolock()`, and `ntfs_attr_vcn_to_rl()` translate or locate VCNs, retrying once after mapping missing runlist fragments.
- `ntfs_attr_lookup()` is the public search API; it dispatches to direct MFT-record search or attribute-list-aware external search.
- `ntfs_attr_open()` initializes an NTFS attribute inode from an attribute record, including resident/non-resident size state, compression/sparse/encryption flags, and named stream handling.
- `ntfs_attr_update_mapping_pairs()` is the central metadata commit path after runlist edits.
- `ntfs_attr_truncate()`, `ntfs_attr_expand()`, `ntfs_attr_map_cluster()`, and `ntfs_attr_fallocate()` expose size growth, allocation, and preallocation behavior.
- `ntfs_attr_rm()`, `ntfs_attr_add()`, `ntfs_attr_remove()`, `ntfs_attr_readall()`, `ntfs_non_resident_attr_insert_range()`, `ntfs_non_resident_attr_collapse_range()`, and `ntfs_non_resident_attr_punch_hole()` provide higher-level metadata operations.

Core mechanics:
- Attribute search relies on NTFS sort order by type, name, and resident value. `ntfs_attr_find()` scans one MFT record and validates record lengths, name bounds, resident value bounds, non-resident mapping-pairs offsets, and minimum resident sizes for known attribute types.
- `ntfs_external_attr_find()` walks `$ATTRIBUTE_LIST`, maps extent MFT records, validates list entries and stale MFT references, and returns both the found attribute record and its attribute-list entry.
- Search contexts carry current MFT record, current attribute, base record state, mapped extent state, and current attribute-list entry. Context reinitialization must unmap extent records and restore base-record pointers safely.
- Runlist mapping decompresses only the needed extent for a VCN unless whole-runlist mapping is requested. Whole mapping enumerates extents by increasing `lowest_vcn`/`highest_vcn` and marks `NInoFullyMapped`.
- Resident-to-non-resident conversion allocates clusters, builds mapping pairs, writes non-resident record fields, updates inode sizes and compressed metadata, then flips `NInoNonResident` only after the record is internally consistent.
- Non-resident-to-resident conversion is attempted for zero-size eligible attributes, with special protection for `$MFT/$BITMAP` and no support for compressed/encrypted conversion.
- Attribute insertion first tries the base MFT record, then existing extents, then creates an attribute list and/or allocates a new extent record. Resident and non-resident record creation update `$ATTRIBUTE_LIST` when present.
- Mapping-pairs update rewrites extents from a runlist, grows/shrinks mapping-pairs storage, may move attributes away, may create new extent records, and marks obsolete extents with `NTFS_VCN_DELETE_MARK` before removal.
- Sparse state is inferred from runlist holes. `ntfs_attr_update_meta()` adds/removes the `compressed_size` field space by moving names and mapping-pairs offsets when an attribute becomes or stops being sparse.
- Truncation paths split by resident/non-resident and grow/shrink. Non-resident growth may append holes for sparse-capable `$DATA` or allocate clusters; shrink frees clusters, truncates runlists, and updates mapping pairs.
- `ntfs_attr_map_cluster()` materializes an LCN for holes or delayed allocations, choosing a seek LCN from neighboring real runs, and either commits mapping pairs immediately or marks the runlist dirty.
- Range insertion/collapse/punch manipulate runlists with helper routines, adjust allocation/data/initialized sizes, update mapping pairs, free punched clusters, and mark filename metadata dirty where needed.
- `ntfs_attr_fallocate()` grows the unnamed data attribute if necessary, optionally restores visible size for keep-size mode, then allocates initialized-range holes and later uninitialized extents.

Important invariants:
- `ni->runlist.lock` must protect mutable runlists; mapping functions document read/write lock requirements.
- MFT records must be mapped/unmapped through search contexts or inode helpers, and dirty records must be marked after metadata changes.
- `$ATTRIBUTE_LIST` presence changes insertion/removal semantics; attribute-list entries must be kept sorted and synchronized with moved or deleted records.
- Attribute extents for a non-resident stream must advance monotonically by VCN and agree with the runlist after mapping-pairs rebuild.
- On-disk size fields, in-memory `allocated_size`, `data_size`, `initialized_size`, `i_blocks`, sparse/compressed flags, and filename dirty state must be updated together.
- Encrypted attributes are rejected by truncate/expand conversion paths; compressed truncation through `ntfs_attr_truncate_i()` is not supported.

Notable risks:
- This file contains many rollback paths where failures can leave leaked clusters or inconsistent metadata; several errors explicitly tell users to run `chkdsk`.
- `ntfs_attr_put_search_ctx()` unmaps `ctx->base_ntfs_ino` when `mapped_base_mrec` is set and current inode differs; this is delicate because external-search state distinguishes mapped base and mapped extent records.
- Some helpers return `-1` instead of a standard negative errno on internal failure, notably `ntfs_non_resident_attr_record_add()`, which callers treat as generic failure.
- `ntfs_non_resident_attr_insert_range()` leaks `hole_rl` on the early `ntfs_attr_map_whole_runlist()` error path after allocation.
- `ntfs_attr_map_cluster()` can defer mapping-pairs updates until low free space or later dirty-runlist flush, so callers must honor `NInoRunlistDirty`.
- Resident resize tries to free space by converting or moving unrelated attributes; this is powerful but increases the blast radius of one attribute resize.
- Range collapse can make an attribute resident when allocation reaches zero; callers need to tolerate representation changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/attrib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/attrib.h -->
# File Research: sources/os/linux/linux/fs/ntfs/attrib.h

Declares the NTFS attribute subsystem interface and the `ntfs_attr_search_ctx` state object used by lookup, mapping, mutation, and enumeration paths.

Key exports:
- `AT_UNNAMED` is the shared sentinel for unnamed attributes.
- `struct ntfs_attr_search_ctx` tracks current/base MFT records, current attribute record, mapped-record ownership, current attribute-list entry, and search continuation state.
- Runlist APIs include `ntfs_map_runlist_nolock()`, `ntfs_map_runlist()`, `ntfs_attr_vcn_to_lcn_nolock()`, `ntfs_attr_find_vcn_nolock()`, `__ntfs_attr_find_vcn_nolock()`, `ntfs_attr_map_whole_runlist()`, `ntfs_attr_vcn_to_rl()`, and `ntfs_attr_map_cluster()`.
- Lookup and context APIs include `ntfs_attr_lookup()`, `load_attribute_list()`, `ntfs_attr_reinit_search_ctx()`, `ntfs_attr_get_search_ctx()`, `ntfs_attr_put_search_ctx()`, and inline `ntfs_attrs_walk()`.
- Attribute sizing and representation APIs include `ntfs_attr_size()`, `ntfs_attr_size_bounds_check()`, `ntfs_attr_can_be_resident()`, `ntfs_attr_record_resize()`, `ntfs_resident_attr_value_resize()`, and `ntfs_attr_make_non_resident()`.
- Mutation APIs include add/remove/read-all/update-mapping-pairs/truncate/expand/fallocate/range insert-collapse-punch functions.

Core mechanics:
- `ntfs_attr_size()` abstracts resident value length versus non-resident data size.
- `ntfs_attrs_walk()` enumerates all attributes by calling `ntfs_attr_lookup(AT_UNUSED, ...)`.
- `HOLES_NO` and `HOLES_OK` define expansion policy for sparse holes.

Important invariants:
- Callers using `ntfs_attr_search_ctx` must account for context pointers moving after runlist mapping.
- Search contexts need explicit release with `ntfs_attr_put_search_ctx()`.
- The header exposes both low-level record edits and high-level operations, so call sites must respect locking comments in `attrib.c`.

Notable risks:
- The API surface is broad and low-level; misuse can bypass attribute-list synchronization, dirty marking, or runlist locking.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/attrib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/attrlist.c -->
# File Research: sources/os/linux/linux/fs/ntfs/attrlist.c

Implements `$ATTRIBUTE_LIST` maintenance for NTFS inodes whose attributes span multiple MFT records.

Key entry points:
- `ntfs_attrlist_need()` checks whether an inode still needs an attribute list by scanning entries for references outside the base MFT record.
- `ntfs_attrlist_update()` writes the in-memory attribute-list buffer back to the `$ATTRIBUTE_LIST` attribute.
- `ntfs_attrlist_entry_add()` inserts a sorted attribute-list entry for a newly added attribute record.
- `ntfs_attrlist_entry_rm()` removes the entry referenced by an attribute search context.

Core mechanics:
- `ntfs_attrlist_need()` returns `1` when any list entry points at an extent MFT record, `0` when all entries are in the base record, and negative errno for invalid state.
- `ntfs_attrlist_update()` opens the `$ATTRIBUTE_LIST` attribute, truncates it to `base_ni->attr_list_size`, writes the in-memory buffer, updates `i_size`, and marks the base inode's list dirty.
- `ntfs_attrlist_update()` has a special `$MFT` recovery path: on `-ENOSPC` while updating `$MFT`'s attribute list, it truncates to zero and retries.
- `ntfs_attrlist_entry_add()` computes an aligned entry size, obtains the source MFT reference and sequence number, finds the sorted insertion point with `ntfs_attr_lookup()`, builds a new list buffer, swaps it into the base inode, and persists via `ntfs_attrlist_update()`.
- `ntfs_attrlist_entry_rm()` allocates a smaller buffer, copies around the removed entry, replaces the old list, and persists the new list.

Important invariants:
- Attribute-list entries are 8-byte aligned and sorted consistently with attribute lookup rules.
- Extent inodes redirect updates to their base inode when `ni->nr_extents == -1`.
- The in-memory `attr_list` and `attr_list_size` are changed only around an update call; add rolls back the pointer and size if persistence fails.

Notable risks:
- `ntfs_attrlist_entry_rm()` replaces `base_ni->attr_list` before `ntfs_attrlist_update()` succeeds, so a write failure leaves the in-memory list already modified.
- Entry validation is much lighter here than in `load_attribute_list()` and `ntfs_external_attr_find()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/attrlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/attrlist.h -->
# File Research: sources/os/linux/linux/fs/ntfs/attrlist.h

Declares the small `$ATTRIBUTE_LIST` maintenance API used by attribute mutation code.

Exports:
- `ntfs_attrlist_need()` tests whether a base inode still requires an attribute list.
- `ntfs_attrlist_entry_add()` adds a list entry for an attribute record.
- `ntfs_attrlist_entry_rm()` removes the list entry described by a search context.
- `ntfs_attrlist_update()` persists the base inode's in-memory attribute-list buffer.

Integration:
- Includes `attrib.h` because removal is keyed by `struct ntfs_attr_search_ctx`.
- Used by `attrib.c` when adding, deleting, moving, and rewriting attribute records.

Notable risks:
- The header exposes no locking contract; callers must follow the surrounding attribute/MFT locking discipline.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/attrlist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/bdev-io.c -->
# File Research: sources/os/linux/linux/fs/ntfs/bdev-io.c

Provides direct block-device I/O helpers for NTFS metadata reads and block-device page-cache writes.

Key entry points:
- `ntfs_bdev_read()` synchronously reads from a block device into a caller buffer.
- `ntfs_bdev_write()` writes a caller buffer into the block device's address-space folios and marks them dirty.

Core mechanics:
- Reads require 512-byte sector alignment for `start`.
- Non-vmalloc read buffers use `bdev_rw_virt()` with `REQ_OP_READ | REQ_META | REQ_SYNC`.
- Vmalloc read buffers are filled by one or more bios using `bio_add_vmalloc_chunk()`, chained when the current bio cannot accept more data.
- Writes go through `sb->s_bdev->bd_mapping`, reading each target folio, copying the relevant byte range, marking it uptodate and dirty, then dropping the folio.

Important invariants:
- Direct read offsets are sector-based; write offsets are page-cache based.
- The write helper assumes the target block-device folios can be read before modification.
- The vmalloc read path must handle multi-bio chunking for large buffers.

Notable risks:
- `ntfs_bdev_read()` checks `if (op == REQ_OP_READ)` before `invalidate_kernel_vmap_range()`, but `op` includes flags, so this condition is false and the vmalloc read buffer is not invalidated through that branch.
- `ntfs_bdev_write()` returns after the first folio read error and does not roll back prior dirty folios.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/bdev-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/bitmap.c -->
# File Research: sources/os/linux/linux/fs/ntfs/bitmap.c

Implements NTFS bitmap mutation and filesystem trim support.

Key entry points:
- `ntfs_trim_fs()` scans the volume LCN bitmap for free clusters and issues discard requests.
- `__ntfs_bitmap_set_bits_in_run()` sets or clears a bit range in a bitmap inode with rollback support.

Core mechanics:
- `ntfs_trim_fs()` converts the requested byte range to cluster bounds, reads bitmap folios, finds zero-bit runs, aligns discards to block-device discard granularity or cluster size, and accumulates the trimmed byte count in `range->len`.
- Bitmap scan windows are page-sized: one page represents `PAGE_SIZE * 8` clusters.
- `__ntfs_bitmap_set_bits_in_run()` maps bitmap folios, handles partial first byte, whole bytes, subsequent pages, and partial final byte.
- When mutating the volume `$Bitmap` (`FILE_Bitmap`), it updates in-memory empty-bit accounting via `ntfs_set_lcn_empty_bits()`.
- On a subsequent-page mapping failure after partial modification, it recursively rolls back the modified prefix by writing the opposite bit value.

Important invariants:
- Bit ranges must have non-negative start/count and value must be 0 or 1.
- Folios are locked, locally mapped, modified, marked dirty, unlocked, and released.
- Rollback mode suppresses another rollback attempt and returns the original error.

Notable risks:
- Trim alignment uses aligned byte ranges inside cluster runs; small or misaligned free runs below `range->minlen` are skipped.
- If rollback fails after a bitmap mutation error, the volume is marked erroneous and metadata may be inconsistent.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/bitmap.h -->
# File Research: sources/os/linux/linux/fs/ntfs/bitmap.h

Declares NTFS bitmap helpers and provides inline convenience wrappers for bit and run updates.

Exports:
- `ntfs_trim_fs()` for FITRIM/discard support.
- `__ntfs_bitmap_set_bits_in_run()` for internal bitmap mutation with rollback mode.
- `ntfs_bitmap_set_bits_in_run()` public wrapper with rollback disabled.
- `ntfs_bitmap_set_run()`, `ntfs_bitmap_clear_run()`, `ntfs_bitmap_set_bit()`, and `ntfs_bitmap_clear_bit()` convenience helpers.

Core mechanics:
- All wrappers reduce to `__ntfs_bitmap_set_bits_in_run()` with `value` set to either 1 or 0.
- The API operates on a VFS inode representing a bitmap attribute.

Notable risks:
- The inline wrappers do no validation; all validation and rollback behavior is centralized in `bitmap.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/collate.c -->
# File Research: sources/os/linux/linux/fs/ntfs/collate.c

Implements NTFS index collation rules used when comparing index keys.

Key entry points:
- `ntfs_collate()` dispatches by collation rule.
- Internal comparators handle binary data, single little-endian ULONGs, arrays of little-endian ULONGs, and file-name keys.

Core mechanics:
- Binary collation compares shared prefix with `memcmp()` and breaks ties by length.
- `COLLATION_NTOFS_ULONG` requires both inputs to be exactly 4 bytes and compares decoded little-endian values.
- `COLLATION_NTOFS_ULONGS` requires equal lengths and 4-byte alignment, then compares decoded `__le32` values in order.
- File-name collation first compares with `IGNORE_CASE` using the volume upcase table, then breaks equal folded names with a case-sensitive comparison.
- Unknown collation rules log an NTFS error and return `-EINVAL`.

Important invariants:
- `ntfs_collate()` returns negative, zero, or positive ordering values, but some error paths use `-EINVAL` or `-1`.
- File-name collation depends on `vol->upcase` and `vol->upcase_len`.

Notable risks:
- `ntfs_collate_ntofs_ulongs()` returns `-1` for invalid lengths after logging, which is indistinguishable from "less than" to callers that do not separately validate.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/collate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/collate.h -->
# File Research: sources/os/linux/linux/fs/ntfs/collate.h

Declares NTFS collation support and validates supported collation rule IDs.

Exports:
- `ntfs_is_collation_rule_supported()` checks support for binary, NTOFS ULONG, NTOFS ULONGS, and file-name collation.
- `ntfs_collate()` compares two data items using a selected NTFS collation rule.

Core mechanics:
- The inline support check first rejects rules outside the implemented set, then verifies the numeric rule is within the standard NTFS supported ranges.
- Consumers can cheaply reject unsupported index collation before attempting comparisons.

Notable risks:
- The support check allows only the implemented rules despite recognizing standard numeric ranges, so any future rule requires both this header and `collate.c` dispatch changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/collate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/compress.c -->
# File Research: sources/os/linux/linux/fs/ntfs/compress.c

Implements NTFS compressed `$DATA` read and write support, including decompression into page-cache pages, LZNT1-like sub-block compression, compressed-block allocation, and compressed writes.

Key entry points:
- `allocate_compression_buffers()` and `free_compression_buffers()` manage the shared 64 KiB compression buffer.
- `ntfs_read_compressed_block()` reads one or more compression blocks overlapping a locked folio and fills page-cache pages.
- `ntfs_compress_write()` writes user data into compression-block-sized page groups and commits compressed blocks through `ntfs_write_cb()`.

Core mechanics:
- A single global `ntfs_compression_buffer` is protected by `ntfs_cb_lock`.
- `ntfs_decompress()` parses NTFS compression sub-blocks. It handles uncompressed sub-blocks, compressed symbol/phrase tokens, overlapping back-references, incomplete sub-block zero fill, destination page finalization, initialized-size zeroing, and overflow detection.
- `ntfs_read_compressed_block()` computes compression-block-aligned VCN and page ranges, grabs non-dirty cache pages, reads physical clusters through the block device mapping, and distinguishes sparse, uncompressed, and compressed compression blocks.
- Sparse compression blocks are zero-filled without disk reads after the first `LCN_HOLE`.
- Uncompressed compression blocks copy the full block directly from the shared buffer into destination pages.
- Compressed blocks call `ntfs_decompress()`, which unlocks the shared buffer before completing pages.
- The compressor uses a hash-chain match finder (`compress_context`) over 4 KiB sub-blocks, lazy parsing, phrase tokens for matches, symbol tokens for literals, and falls back to uncompressed storage when compressed output is not smaller.
- `ntfs_write_cb()` maps the input pages, compresses each 4 KiB sub-block, recognizes all-zero compressed output as a sparse block, punches the existing compression block run, allocates new clusters for compressed or uncompressed output, updates mapping pairs, then writes bios.
- `ntfs_compress_write()` expands compressed files to compression-block boundaries as needed, faults in the source iterator, reads and locks every page in the affected compression block, overlays user bytes, writes the block, then unlocks/releases pages.

Important invariants:
- NTFS compression block size is derived from the attribute compression unit and must fit the supported maximum of 64 KiB.
- The decompressor assumes `PAGE_SIZE >= 4096`.
- Compressed I/O is only valid for unnamed `$DATA`; other attributes fail the read path.
- Page finalization must zero regions beyond initialized size and mark pages uptodate before unlocking.
- `ntfs_write_cb()` replaces the whole compression block allocation, not just the modified bytes.
- Mapping pairs must be updated after punching and allocating replacement compressed runs.

Notable risks:
- `ntfs_decompress()` calls `ntfs_error(NULL, ...)`; `__ntfs_error()` only marks volume errors when an `sb` is provided, so stream corruption reported here is not tied to a mounted volume.
- The shared compression buffer serializes compressed reads and writes through one mutex.
- `ntfs_compress_block()` documents `0` as error but returns `-ENOMEM` through an unsigned return type on allocation failure; callers treat nonzero large values as compression failure only indirectly through size checks.
- `ntfs_write_cb()` marks filename/MFT dirty even on several error exits after partial metadata operations.
- Compressed writes rewrite whole compression blocks and depend on page-cache state for unchanged bytes; stale or failed page reads can abort the entire block write.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/debug.c -->
# File Research: sources/os/linux/linux/fs/ntfs/debug.c

Implements NTFS logging helpers and optional debug-only runlist dumping.

Key entry points:
- `__ntfs_warning()` emits warning messages with optional superblock device context.
- `__ntfs_error()` emits error messages and calls `ntfs_handle_error()` when a superblock is supplied.
- Under `DEBUG`, `__ntfs_debug()` emits debug messages when `debug_msgs` is enabled.
- Under `DEBUG`, `ntfs_debug_dump_runlist()` prints a runlist with readable labels for negative sentinel LCNs.

Core mechanics:
- Uses `struct va_format` to pass variadic messages to kernel `pr_warn`, `pr_err`, or `pr_debug`.
- Non-DEBUG warning/error messages are rate-limited; DEBUG builds are not rate-limited.
- Error logging with an `sb` triggers filesystem error handling.
- Runlist dumping iterates until a zero-length terminator and labels `LCN_DELALLOC`, `LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`, or unknown negative LCNs.

Important invariants:
- `ntfs_debug_dump_runlist()` assumes caller-side synchronization for the runlist.
- `debug_msgs` gates DEBUG logging globally.

Notable risks:
- Calls to `ntfs_error()` with `sb == NULL` log but do not trigger `ntfs_handle_error()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/debug.h -->
# File Research: sources/os/linux/linux/fs/ntfs/debug.h

Declares NTFS logging macros and debug-only helpers.

Exports:
- `ntfs_debug()` maps to `__ntfs_debug()` in DEBUG builds and to a compile-time no-op wrapper otherwise.
- `ntfs_debug_dump_runlist()` is available only in DEBUG builds and becomes a no-op otherwise.
- `ntfs_warning()` wraps `__ntfs_warning()` with `__func__`.
- `ntfs_error()` wraps `__ntfs_error()` with `__func__`.
- `ntfs_handle_error()` is declared for error escalation.

Core mechanics:
- Non-DEBUG no-op macros still type-check format arguments through unreachable `no_printk()` branches.
- Logging helpers include the calling function automatically.

Notable risks:
- Whether an error marks the volume depends on callers passing a non-NULL superblock to `ntfs_error()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/debug.h -->