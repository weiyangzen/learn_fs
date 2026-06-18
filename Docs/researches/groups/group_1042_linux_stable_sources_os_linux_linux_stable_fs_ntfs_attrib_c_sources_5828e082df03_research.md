# Group Research: group_1042_linux_stable_sources_os_linux_linux_stable_fs_ntfs_attrib_c_sources_5828e082df03

Scope: `Docs/research_subset_a.md`  
Files read completely: yes

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/attrib.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/attrib.c

Purpose: Core NTFS attribute implementation. This file owns attribute lookup, runlist mapping, resident/non-resident conversion, attribute creation/removal, mapping-pair persistence, truncate/expand/fallocate behavior, range insert/collapse/punch operations, and whole-attribute reads.

Key responsibilities:
- Maps virtual cluster numbers to runlist/LCN state through `ntfs_map_runlist_nolock()`, `ntfs_map_runlist()`, `ntfs_attr_vcn_to_lcn_nolock()`, `ntfs_attr_find_vcn_nolock()`, and `ntfs_attr_map_whole_runlist()`.
- Searches MFT attributes with `ntfs_attr_find()`, `ntfs_external_attr_find()`, and `ntfs_attr_lookup()`, including attribute-list-backed extents and continuation semantics through `struct ntfs_attr_search_ctx`.
- Validates attribute record bounds aggressively: record length, name offset, resident value offset/length, nonresident mapping-pair offset, minimum value sizes for known resident attributes, and attribute-list ordering.
- Converts attributes between resident and non-resident forms via `ntfs_attr_make_non_resident()` and `ntfs_attr_make_resident()`.
- Adds, removes, resizes, and moves attribute records with `ntfs_attr_record_resize()`, `ntfs_resident_attr_record_add()`, `ntfs_non_resident_attr_record_add()`, `ntfs_attr_record_rm()`, `ntfs_attr_add()`, `ntfs_attr_record_move_to()`, and `ntfs_attr_record_move_away()`.
- Rebuilds mapping pairs and attribute extents with `ntfs_attr_update_mapping_pairs()`, including sparse/compressed metadata updates and allocation of new extent MFT records when mapping pairs no longer fit.
- Handles size changes through `ntfs_attr_expand()`, `ntfs_attr_truncate_i()`, `ntfs_attr_truncate()`, `__ntfs_attr_truncate_vfs()`, `ntfs_non_resident_attr_expand()`, `ntfs_non_resident_attr_shrink()`, and `ntfs_resident_attr_resize()`.
- Implements cluster materialization for holes/delalloc via `ntfs_attr_map_cluster()` and higher-level allocation through `ntfs_attr_fallocate()`.
- Supports range operations for nonresident unnamed `$DATA`: `ntfs_non_resident_attr_insert_range()`, `ntfs_non_resident_attr_collapse_range()`, and `ntfs_non_resident_attr_punch_hole()`.
- Provides convenience helpers for attribute existence/removal/read-all/name conversion.

Important data and invariants:
- `AT_UNNAMED` is the canonical unnamed attribute marker.
- Runlist updates require correct locking: most mapping paths require `ni->runlist.lock`; conversion/truncate/fallocate also interact with `mrec_lock`.
- Search contexts may map base and extent MFT records and must be released with `ntfs_attr_put_search_ctx()`.
- Attribute-list presence changes lookup semantics; operations must keep `base_ni->attr_list`, on-disk `$ATTRIBUTE_LIST`, and per-record attribute entries synchronized.
- First nonresident attribute extent carries allocated/data/initialized/compressed size metadata.
- Sparse state is inferred from runlist contents and mirrored into inode flags, attribute flags, compressed-size field presence, and filename-dirty state.
- `$MFT::$DATA` is protected from truncate/expand paths.
- Encrypted attributes are largely unsupported for resize/truncate and return errors.

Key dependencies:
- `attrlist.c` for attribute-list entry add/remove/update.
- `lcnalloc` and runlist helpers for cluster allocation, freeing, merging, truncation, sparse detection, and mapping-pair build/decompress.
- `mft` and inode helpers for MFT record mapping, extent allocation, dirty marking, inode open/close, and attrlist creation.
- `iomap`/direct I/O zeroing for fallocate hole materialization.

Error handling and risk notes:
- Many corruption paths convert lookup or mapping failures to `-EIO` and set volume errors for chkdsk-style recovery.
- Rollback is best-effort in resident-to-nonresident conversion and nonresident expansion; failures can leave leaked clusters or inconsistent metadata, with explicit error logs.
- Several paths intentionally continue after cleanup failures to preserve metadata consistency as much as possible.
- `ntfs_resident_attr_record_add()` and `ntfs_non_resident_attr_record_add()` return offsets on success, but some failure paths normalize to `-EIO` or `-1`; callers must not assume all errno values are preserved.
- `ntfs_attr_update_mapping_pairs()` is central and high risk: it can resize records, move attributes, add attrlists, allocate new extents, delete obsolete extents, and update compressed/sparse accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/attrib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/attrib.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/attrib.h

Purpose: Public interface and shared structures for NTFS attribute handling.

Key contents:
- Declares `AT_UNNAMED`.
- Defines `struct ntfs_attr_search_ctx`, the state object used by attribute lookup and enumeration.
- Defines hole expansion policy enum: `HOLES_NO` and `HOLES_OK`.
- Declares runlist mapping, VCN lookup, attribute lookup, search-context lifecycle, size bounds, record resize, resident value resize, resident/nonresident conversion, truncate/expand/fallocate, range mutation, add/remove/existence, attrlist-sensitive record moves, name conversion, read-all, and mapping-pair update APIs.
- Provides `ntfs_attr_size()` inline helper to return resident value length or nonresident data size.
- Provides `ntfs_attrs_walk()` inline enumeration helper over `ntfs_attr_lookup(AT_UNUSED, ...)`.

Important invariants:
- `ntfs_attr_search_ctx` carries both current and base MFT-record state so callers can traverse attributes split across extent records.
- Callers using lookup/enumeration must preserve and release search contexts correctly because contexts can map MFT records.
- Header exposes several low-level mutation APIs, so locking requirements are documented mainly in `attrib.c` rather than enforced by the type system.

Dependencies:
- Includes `ntfs.h` and `dir.h`.
- Tightly coupled to MFT record layout, attribute-list entries, and runlist structures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/attrib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/attrlist.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/attrlist.c

Purpose: Maintains NTFS `$ATTRIBUTE_LIST` contents for files whose attributes span multiple MFT records.

Key responsibilities:
- `ntfs_attrlist_need()` decides whether an inode still needs an attribute list by checking whether any list entry references an MFT record other than the base inode.
- `ntfs_attrlist_update()` opens the `$ATTRIBUTE_LIST` attribute, resizes it to `base_ni->attr_list_size`, writes the in-memory list to disk, handles a special `$MFT` ENOSPC retry path, and marks attrlist state dirty.
- `ntfs_attrlist_entry_add()` allocates a larger in-memory attrlist, finds the sorted insertion point using attribute lookup, builds a new `struct attr_list_entry`, copies old entries around it, updates `base_ni->attr_list`, and persists via `ntfs_attrlist_update()`.
- `ntfs_attrlist_entry_rm()` removes the current `ctx->al_entry` from the base inode’s in-memory attrlist and persists the resized list.

Important invariants:
- Attribute-list entries are sorted according to the same lookup/collation rules used by `ntfs_attr_lookup()`.
- Entry length is 8-byte aligned and includes any Unicode name payload.
- `mft_reference` uses the containing MFT record number and sequence number.
- If the update fails after add, the old list pointer and size are restored.

Dependencies:
- Uses `attrib.c` lookup/truncate/write paths to find insertion points and persist the list.
- Uses `mft.h` for MFT mapping and sequence-number reference construction.

Risk notes:
- `ntfs_attrlist_need()` assumes valid in-memory list entry lengths; corruption validation is handled elsewhere.
- `ntfs_attrlist_entry_rm()` replaces the list before calling `ntfs_attrlist_update()`, so persistence failure leaves the in-memory list already modified.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/attrlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/attrlist.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/attrlist.h

Purpose: Header exporting attribute-list maintenance APIs.

Exports:
- `ntfs_attrlist_need()`
- `ntfs_attrlist_entry_add()`
- `ntfs_attrlist_entry_rm()`
- `ntfs_attrlist_update()`

Dependencies:
- Includes `attrib.h`, because APIs use `struct ntfs_attr_search_ctx`, `struct ntfs_inode`, and `struct attr_record`.

Role in subsystem:
- This is the narrow bridge from core attribute mutation code to `$ATTRIBUTE_LIST` persistence.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/attrlist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/bdev-io.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/bdev-io.c

Purpose: Direct block-device I/O helpers for NTFS metadata paths.

Key responsibilities:
- `ntfs_bdev_read()` reads byte ranges from a block device using synchronous metadata BIOs. It requires 512-byte sector alignment and uses `bdev_rw_virt()` for non-vmalloc buffers; vmalloc buffers are handled by BIOs built from vmalloc chunks.
- `ntfs_bdev_write()` writes a byte range through the block device page cache by reading target folios, copying into them, marking them uptodate and dirty, and releasing them.

Important behavior:
- Read path sets `REQ_META | REQ_SYNC`.
- Vmalloc read path chains BIOs if one BIO cannot accept the remaining vmalloc chunk.
- After vmalloc read, `invalidate_kernel_vmap_range()` is called.
- Write path does not submit synchronously; it marks block-device mapping folios dirty.

Risk notes:
- `ntfs_bdev_read()` rejects unaligned starts but does not explicitly reject unaligned sizes.
- `ntfs_bdev_write()` assumes `start + size` arithmetic is valid and does not perform sector-alignment checks.
- Write path depends on later writeback for persistence.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/bdev-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/bitmap.c

Purpose: NTFS bitmap manipulation and filesystem trim support.

Key responsibilities:
- `ntfs_trim_fs()` scans the volume LCN bitmap for free cluster runs, aligns discard ranges to block-device discard granularity, issues `blkdev_issue_discard()`, and reports total trimmed bytes in `range->len`.
- `__ntfs_bitmap_set_bits_in_run()` sets or clears arbitrary bit ranges in a bitmap inode, spanning folios as needed, with rollback on later folio-mapping failure.

Important behavior:
- Bitmap bits are little-endian bit positions within bytes.
- Folios are read, locked, locally mapped, modified, marked dirty, unlocked, and put.
- For `FILE_Bitmap`, updates call `ntfs_set_lcn_empty_bits()` to keep volume free-space accounting or auxiliary empty-bit state in sync.
- Partial first/last bytes are handled bit-by-bit; full bytes are changed with `memset()`.
- Rollback recursively restores already-modified bits if a subsequent page fails to map.

Risk notes:
- Trim operates page-by-page over the bitmap and relies on zero bits meaning free clusters.
- Rollback failure marks the volume erroneous because metadata may be inconsistent.
- `WARN_ON(cnt > 7)` documents the expected final partial-byte invariant.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/bitmap.h

Purpose: Public bitmap API and convenience wrappers.

Exports:
- `ntfs_trim_fs()`
- `__ntfs_bitmap_set_bits_in_run()`

Inline helpers:
- `ntfs_bitmap_set_bits_in_run()` wraps the internal implementation with rollback disabled.
- `ntfs_bitmap_set_run()` sets a range of bits.
- `ntfs_bitmap_clear_run()` clears a range of bits.
- `ntfs_bitmap_set_bit()` sets one bit.
- `ntfs_bitmap_clear_bit()` clears one bit.

Dependencies:
- Includes Linux fs declarations and NTFS volume definitions.
- Designed for bitmap inode callers that should not need to pass rollback state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/collate.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/collate.c

Purpose: Implements NTFS index collation rules used to compare keys in sorted metadata structures.

Supported rules:
- Binary byte collation via `ntfs_collate_binary()`.
- Single little-endian ULONG collation via `ntfs_collate_ntofs_ulong()`.
- Array of little-endian ULONGs via `ntfs_collate_ntofs_ulongs()`.
- Filename collation via `ntfs_collate_file_name()`, first case-insensitive then case-sensitive.

Public entry point:
- `ntfs_collate()` dispatches based on `COLLATION_*` rule and returns negative/zero/positive ordering or `-EINVAL` for unknown/invalid comparisons.

Important behavior:
- Binary collation compares common prefix, then shorter length sorts first.
- ULONG collation validates exact 4-byte length.
- ULONG-array collation requires equal lengths and 4-byte alignment.
- Filename collation uses the NTFS upcase table from the volume.

Risk notes:
- `ntfs_collate_ntofs_ulongs()` logs invalid lengths and returns `-1`, which can look like “less than” rather than a distinct error to callers.
- Unknown collation rules are explicitly logged and rejected.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/collate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/collate.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/collate.h

Purpose: Header for NTFS collation support.

Key contents:
- `ntfs_is_collation_rule_supported()` validates supported collation constants and accepted numeric ranges.
- Declares `ntfs_collate()`.

Supported rules:
- `COLLATION_BINARY`
- `COLLATION_NTOFS_ULONG`
- `COLLATION_FILE_NAME`
- `COLLATION_NTOFS_ULONGS`

Role:
- Used by index parsing/search code to reject unsupported on-disk collation modes before comparing keys.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/collate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/compress.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/compress.c

Purpose: Handles NTFS compressed attribute reads and writes, including LZNT1-style compression/decompression, sparse compression blocks, and compressed-block disk allocation.

Key responsibilities:
- Manages a global decompression buffer with `allocate_compression_buffers()` and `free_compression_buffers()`, protected by `ntfs_cb_lock`.
- `ntfs_decompress()` parses compressed blocks into destination pages, handling uncompressed sub-blocks, compressed phrase/symbol tokens, overlapping phrase copies, incomplete sub-block zero-fill, page finalization, and initialized-size zeroing.
- `ntfs_read_compressed_block()` reads all pages in the compression block containing a requested folio, resolves runlist mappings, reads compressed clusters from the block device mapping, distinguishes sparse/uncompressed/compressed compression blocks, and fills/updates/unlocks page-cache pages.
- Compression write path uses `ntfs_best_match()`, `ntfs_skip_position()`, and `ntfs_compress_block()` to encode 4 KiB sub-blocks.
- `ntfs_write_cb()` compresses one compression block, chooses compressed, sparse-all-zero, or uncompressed storage, punches the old block, allocates new clusters, updates mapping pairs, and submits write BIOs.
- `ntfs_compress_write()` updates compressed file data from an iov iterator by reading all pages in each compression block, copying user data into them, writing the recompressed block, and releasing pages.

Important data and constants:
- Compression block maximum is 64 KiB.
- NTFS sub-block size is 4096 bytes.
- Token type constants distinguish symbol and phrase tokens.
- Match finder uses a hash table and short chain depth limit for write-side compression.
- Predefined compressed zero sequences are used to detect all-zero blocks and represent them as sparse.

Important invariants:
- Decompression requires page size at least 4096.
- Only unnamed `$DATA` compressed attributes are accepted by the read path.
- The global compression buffer is protected while reading/decompressing compressed data; `ntfs_decompress()` unlocks it when safe.
- Pages that were dirty or uptodate are not overwritten during compressed reads.
- Compressed writes operate at full compression-block granularity.

Dependencies:
- Uses attribute/runlist functions from `attrib.c`.
- Uses cluster allocation/freeing and runlist merge from allocation/runlist subsystems.
- Uses MFT dirty marking and file-name dirty state for metadata updates.
- Uses block-device mapping pages for reads and BIOs for writes.

Risk notes:
- Decompression failure returns `-EOVERFLOW` internally and usually becomes `-EIO` at the read entry point if the requested page was not completed.
- `ntfs_compress_block()` is documented as returning 0 on error, but allocation failure returns `-ENOMEM` through an unsigned return type; callers treat nonzero large values as a compression failure condition indirectly.
- `ntfs_write_cb()` punches old clusters before allocating/writing replacement clusters, so failures after punching are metadata-sensitive.
- Compression write path marks folios uptodate/clears dirty for fully processed pages but returns bytes written or negative errno depending on final state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/debug.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/debug.c

Purpose: NTFS logging and debug-only runlist dump support.

Key responsibilities:
- `__ntfs_warning()` formats warning messages with optional superblock device context. In non-debug builds it uses ratelimited warnings.
- `__ntfs_error()` formats error messages with optional superblock device context. In non-debug builds it uses ratelimited errors and calls `ntfs_handle_error(sb)` when a superblock is present.
- Under `DEBUG`, defines global `debug_msgs`, implements `__ntfs_debug()`, and provides `ntfs_debug_dump_runlist()`.

Important behavior:
- Logging wrappers include the caller function name via macros in `debug.h`.
- `ntfs_debug_dump_runlist()` prints VCN, LCN or symbolic negative LCN state, and run length until the terminating zero-length element.
- Debug output is controlled at runtime by `debug_msgs` when compiled with `DEBUG`.

Dependencies:
- Includes `debug.h`, which includes runlist declarations.
- `ntfs_handle_error()` is declared in `debug.h` and implemented elsewhere.

Risk notes:
- Error logging has side effects through `ntfs_handle_error(sb)`, so `ntfs_error()` is not just diagnostic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/debug.h -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/debug.h

Purpose: Logging macro interface for NTFS code.

Key contents:
- In `DEBUG` builds, declares `debug_msgs`, `__ntfs_debug()`, and maps `ntfs_debug()` to include file, line, and function.
- In non-debug builds, `ntfs_debug()` and `ntfs_debug_dump_runlist()` compile to no-op constructs that still type-check format arguments.
- Declares `__ntfs_warning()` and `__ntfs_error()` with printf format attributes.
- Defines `ntfs_warning()` and `ntfs_error()` macros that inject `__func__`.
- Declares `ntfs_handle_error()`.

Role:
- Centralizes NTFS diagnostics and ensures errors can trigger filesystem error handling while warnings remain diagnostic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/debug.h -->