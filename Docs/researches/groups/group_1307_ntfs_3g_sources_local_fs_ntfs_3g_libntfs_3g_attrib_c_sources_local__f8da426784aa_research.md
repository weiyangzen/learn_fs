# Group Research: group_1307_ntfs_3g_sources_local_fs_ntfs_3g_libntfs_3g_attrib_c_sources_local__f8da426784aa

Scope: `Docs/research_subset_a.md`. This grouped report covers the listed NTFS-3G library files under `sources/local-fs/ntfs-3g/libntfs-3g/`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/attrib.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/attrib.c

## Scope

Implements NTFS attribute handling for libntfs-3g: opening attributes, resolving attribute-list extents, mapping VCNs to LCNs, reading/writing resident and non-resident data, resizing/truncating attributes, converting residency, updating mapping pairs, adding/removing attribute records, and validating on-disk attribute structure.

## API And Behavior

- Exports special NTFS Unicode names/constants: `AT_UNNAMED`, `STREAM_SDS`, and `TXF_DATA`.
- Attribute flag helpers expose compressed/encrypted/sparse state, but only allow inode file-attribute flag changes for unnamed `$DATA`.
- `ntfs_get_attribute_value_length()` and `ntfs_get_attribute_value()` read raw attribute values from an `ATTR_RECORD`; non-resident reads decompress mapping pairs and read clusters directly, with explicit limitations around compressed/sparse data and attribute lists.
- `ntfs_attr_open()` allocates and initializes `ntfs_attr`, validates names and flags, handles empty-stream compression policy, initializes resident/non-resident sizes, rejects unsupported compression units, and enforces consistency between unnamed `$DATA` flags and inode flags.
- `ntfs_attr_close()` releases runlists and dynamically duplicated names while preserving internal constant names.
- Runlist helpers include `ntfs_attr_map_runlist()`, optional `ntfs_attr_map_partial_runlist()`, `ntfs_attr_map_whole_runlist()`, `ntfs_attr_vcn_to_lcn()`, and `ntfs_attr_find_vcn()`. They lazily decompress mapping pairs, handle attribute extents, detect corrupt attribute lists, and mark fully mapped attributes.
- `ntfs_attr_pread()` reads resident values from MFT records or non-resident data through runlists. It zero-fills holes/uninitialized ranges, supports compressed reads only through `ntfs_compressed_attr_pread()`, denies encrypted non-resident reads unless `efs_raw` is enabled, and adds raw-EFS padding bytes in raw mode.
- `ntfs_attr_pwrite()` writes resident data into the MFT record or non-resident data through runlists. It extends attributes when needed, fills gaps with zeroes, allocates holes, supports compressed write paths one compression block at a time, updates mapping pairs, and attempts rollback of data/initialized sizes on failures.
- `ntfs_attr_pclose()` finalizes compressed non-resident attributes by compressing the terminal block and updating mapping pairs.
- `ntfs_attr_mst_pread()` and `ntfs_attr_mst_pwrite()` wrap attribute I/O with multi-sector transfer fixup/deprotect logic for records protected by NTFS update sequence arrays.
- `ntfs_attr_lookup()` dispatches to `ntfs_attr_find()` for single-record searches or `ntfs_external_attr_find()` when an attribute list is present. It supports enumeration with `AT_UNUSED`, insertion positioning on `ENOENT`, named/unnamed matching, value matching for resident attributes, and extent lookup by `lowest_vcn`.
- `ntfs_attr_inconsistent()` performs structural checks on resident and non-resident attributes and hard-coded well-known attribute constraints for file names, index roots, standard information, object IDs, volume attributes, and index allocation.
- Attribute definition helpers enforce `$AttrDef` size bounds, non-residency permission, resident permission, and special-case Windows compatibility rules such as resident `$LOGGED_UTILITY_STREAM:$TXF_DATA`.
- Record mutation helpers include `ntfs_make_room_for_attr()`, resident/non-resident record adders, `ntfs_attr_record_rm()`, `ntfs_attr_add()`, `ntfs_attr_set_flags()`, `ntfs_attr_rm()`, `ntfs_attr_record_resize()`, `ntfs_resident_attr_value_resize()`, and record movement between MFT extents.
- Residency conversion helpers convert resident attributes to non-resident records, force non-residency, convert non-resident attributes back to resident when allowed, and may move other attributes or create attribute lists to free MFT record space.
- `ntfs_attr_update_mapping_pairs()` rewrites mapping pairs from in-memory runlists, updates sparse/compressed metadata, adds/removes attribute extents, and can allocate new MFT records for overflow mapping pairs.
- Truncation paths shrink or expand resident and non-resident attributes, create holes for NTFS 3+ `$DATA`, avoid holes in solid truncation, maintain file-name/index size metadata, and special-case compressed files.
- Convenience helpers read/write data streams, shrink data size without freeing allocation, check/remove attribute existence, and count free bits in bitmap attributes.

## State And Dependencies

The file is the central coordinator between `ntfs_attr`, `ntfs_inode`, `MFT_RECORD`, `ATTR_RECORD`, attribute lists, runlists, cluster allocation, compression, MST fixups, volume geometry, `$AttrDef`, and device I/O. It depends heavily on endian conversions, MFT dirty flags, runlist sentinels (`LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`), and inode state flags such as `NInoAttrList`, `NAttrRunlistDirty`, `NAttrFullyMapped`, `NAttrDataAppending`, and `NAttrBeingNonResident`.

## Risks And Invariants

Many operations mutate several structures that must stay synchronized: runlists, mapping pairs, allocated/data/initialized/compressed sizes, sparse/compressed flags, attribute-list entries, MFT record layout, and filename/index cached sizes. The code contains explicit partial-failure warnings where rollback is incomplete and metadata may be left inconsistent, especially around bitmap/runlist updates, mapping-pair rebuilds, resident/non-resident conversion, cluster freeing, and compressed writes. Encrypted non-resident attributes are mostly unsupported outside raw EFS mode. Compressed writes are constrained to supported NTFS compression mode and often one compression block at a time. Updating mapping pairs from nonzero `from_vcn` has documented sparse/compressed-size limitations.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/attrib.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/attrlist.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/attrlist.c

## Scope

Manages `$ATTRIBUTE_LIST` contents for inodes whose attributes span multiple MFT records.

## API And Behavior

- `ntfs_attrlist_need()` checks whether any attribute-list entry points outside the base inode MFT reference; if all entries point to the base record, the attribute list is no longer needed.
- `ntfs_attrlist_entry_add()` creates an aligned `ATTR_LIST_ENTRY` from an `ATTR_RECORD`, finds the sorted insertion point using `ntfs_attr_lookup()`, resizes the `$ATTRIBUTE_LIST` attribute, builds a new in-memory list buffer, inserts the entry, swaps it into `ni->attr_list`, updates `attr_list_size`, and marks the list dirty.
- `ntfs_attrlist_entry_rm()` removes `ctx->al_entry` from the base inode attribute list, resizes `$ATTRIBUTE_LIST`, copies all remaining entries into a new buffer, replaces `base_ni->attr_list`, and marks the list dirty.

## State And Dependencies

The file depends on `ntfs_inode` base/extent relationships, `ATTR_LIST_ENTRY`, `ATTR_RECORD`, attribute search contexts, `ntfs_attr_open()`, `ntfs_attr_truncate()`, and dirty tracking through `NInoAttrListSetDirty()`.

## Risks And Invariants

Attribute-list entries must remain sorted and 8-byte aligned. The code assumes existing in-memory list entries are well formed when iterating by `length`; corrupt lengths can break traversal. Add/remove operations resize the on-disk `$ATTRIBUTE_LIST` first and then replace the in-memory buffer, so errors after resize are sensitive and rely on callers/filesystem repair paths to recover.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/attrlist.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/bitmap.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/bitmap.c

## Scope

Provides low-level bitmap bit accessors and attribute-backed run set/clear helpers for NTFS bitmap attributes.

## API And Behavior

- `ntfs_bit_set()` sets or clears one bit in a byte-addressed bitmap and silently ignores NULL bitmap pointers or invalid bit values.
- `ntfs_bit_get()` returns a single bit value or `-1` for a NULL bitmap.
- `ntfs_bit_get_and_set()` atomically reads a bit and updates it when needed, returning `-1` for invalid inputs.
- `ntfs_bitmap_set_bits_in_run()` is the shared implementation for setting or clearing a run of bits in an `ntfs_attr`. It handles partial first and last bytes by reading existing bytes, writes up to 8 KiB windows, and loops until the requested run is updated.
- `ntfs_bitmap_set_run()` and `ntfs_bitmap_clear_run()` wrap the shared helper with tracing.

## State And Dependencies

The file uses `ntfs_attr_pread()` and `ntfs_attr_pwrite()` to modify bitmap attributes, with local heap buffers allocated through NTFS helpers. Bit numbering is little-endian within each byte: bit `n` maps to byte `n >> 3` and mask `1 << (n & 7)`.

## Risks And Invariants

No bounds checks are performed by the single-bit helpers. The run update path has known partial-I/O danger points: failed last-byte reads or window writes can leave bitmap metadata inconsistent, and comments explicitly note missing rollback. `count == 0` is accepted by argument validation but drives edge arithmetic through the shared helper, so callers should avoid relying on it as a no-op unless tested.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/bootsect.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/bootsect.c

## Scope

Validates an NTFS boot sector and parses it into `ntfs_volume` geometry fields.

## API And Behavior

- `ntfs_boot_sector_is_ntfs()` verifies the OEM ID signature, bytes per sector range, sectors-per-cluster encoding, maximum cluster size, FAT/reserved BPB fields being zero, MFT/index record cluster-size encodings, non-overlapping positive `$MFT`/`$MFTMirr` LCNs, and optionally logs a warning for a bad `0xaa55` sector marker.
- `ntfs_boot_sector_parse()` populates sector size, cluster size, cluster count, MFT/MFT mirror LCNs, MFT record size, INDX record size, and MFT mirror record count. It validates power-of-two geometry, nonzero sector count, MFT locations within the volume, and seeks to the final sector to catch undersized devices or partition/RAID setup problems.

## State And Dependencies

The parser writes directly into `ntfs_volume`, uses the device operation table for the final-sector seek, relies on little-endian boot sector fields, and logs detailed diagnostics for invalid geometry.

## Risks And Invariants

Validation and parsing are split: callers should run signature/format validation before trusting parsed fields. The final-sector seek is a practical device-size check, not a data read. Negative boot-sector encodings for MFT/INDX record sizes are interpreted as powers of two, matching NTFS format rules.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/bootsect.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/cache.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/cache.c

## Scope

Implements generic fixed-size LRU caches used by NTFS-3G for inode, directory lookup, security ID, and permissions-related cached records.

## API And Behavior

- Cache entries are `CACHED_GENERIC` records with mandatory list fields, fixed payload storage, and optional variable-size allocation.
- Hash support is optional. `inserthashindex()` and `drophashindex()` maintain separate hash-entry chains; bad hash values or inconsistent chains disable hashing and fall back to sequential LRU scans.
- `ntfs_fetch_cache()` searches by hash when available or by LRU scan otherwise, increments read/hit counters, and promotes found entries to the most-recent position.
- `ntfs_enter_cache()` finds or creates an entry, reuses the oldest entry when full, copies fixed and variable payload data, invokes per-entry cleanup on eviction, and inserts a hash index if enabled.
- `ntfs_invalidate_cache()` removes all matching entries, using hash lookup unless `CACHE_NOHASH` is requested, then relinks entries onto the free list and optionally calls the cleanup hook.
- `ntfs_remove_cache()` removes a known entry directly.
- `ntfs_create_cache()` allocates one contiguous block containing the header, entries, optional hash entries, and optional hash buckets.
- `ntfs_create_lru_caches()` initializes volume-level caches according to compile-time cache size macros.
- `ntfs_free_lru_caches()` releases all volume-level caches and any variable data still attached to entries.

## State And Dependencies

The cache layer stores no NTFS semantics itself; behavior is supplied through compare, free, and hash callbacks. Volume cache fields include inode, named-data, lookup, security-ID, and legacy-permissions caches depending on build-time macros.

## Risks And Invariants

The design intentionally does not surface allocation/cache errors to callers; memory pressure simply makes entries uncached. Hashing can be disabled at runtime after internal consistency problems, preserving correctness through slower sequential scans. The implementation assumes at least enough entries for LRU reuse semantics and that callers do not free returned cache entries directly.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/cache.c -->