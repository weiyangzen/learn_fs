# Group Research: group_1875_xfsprogs_sources_local_fs_xfsprogs_libxfs_xfs_attr_leaf_c_sources_l_9ae255906e83

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/xfsprogs`. All listed files were read completely. Line/byte counts matched the work item manifest.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_leaf.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_leaf.c

## Purpose

`xfs_attr_leaf.c` implements XFS extended-attribute shortform storage and attr leaf-block operations for libxfs. It covers inline attr fork management, conversion between shortform/leaf/node formats, leaf block verification, sorted-hash lookup, insertion/removal, compaction, split/rebalance/join support, and `INCOMPLETE` flag handling for atomic replace and remote-value updates.

## Main Behavior

The file normalizes legacy and CRC-enabled attr leaf headers through `xfs_attr3_leaf_hdr_from_disk` and `xfs_attr3_leaf_hdr_to_disk`, using a 32-bit in-core `firstused` field so 64 KiB attr blocks can round-trip through 16-bit on-disk headers. Leaf verifiers check da block metadata, CRCs, owner fields, hash ordering, name/value bounds, remote entry validity, free-map alignment, bounds, and overlap.

Shortform attrs live inside the inode attr fork. The shortform code creates the fork, checks fork byte fit, finds/replaces/adds/removes entries, copies values, verifies packed inline layout, removes the attr fork when it becomes empty, and converts shortform attrs into a newly allocated leaf block. Parent-pointer attrs get special value matching and replacement handling.

Leaf blocks use a sorted entry array at the front of the block and a backward-growing name/value region at the end. `xfs_attr3_leaf_add` finds free space, compacts fragmented blocks when useful, and inserts local or remote entries. Local entries store name and value in the leaf; remote entries store only the name and create an incomplete placeholder with remote block fields filled later by remote-value code.

The file also supports leaf-to-node conversion, split-time rebalance, block ordering, leaf coalescing decisions, removal, unbalance into a sibling, last-hash extraction, and duplicate-hash lookup. Lookup returns `-EEXIST` for found and `-ENOATTR` for not found, while also recording the entry index or insertion point in `args->index`.

## Atomic Replace and Remote Values

`xfs_attr3_leaf_setflag`, `xfs_attr3_leaf_clearflag`, and `xfs_attr3_leaf_flipflags` manage visibility through `XFS_ATTR_INCOMPLETE`. Remote attrs remain incomplete until remote blocks are allocated and synchronously written. Replace can flip old/new entries in one transaction, including the case where they are in different leaf blocks.

## Dependencies and Risks

This file depends on libxfs da btree, bmap, transaction, inode fork, remote attr, health, tracing, and on-disk format definitions. Risky areas are `firstused` overflow conversion, free-map coalescing/overlap behavior, duplicate hashes, old/new index tracking during split and replace, shortform/leaf format transitions during logged operations, and ensuring incomplete remote entries are never exposed before their values are durable.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_leaf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_leaf.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_leaf.h

## Purpose

`xfs_attr_leaf.h` declares the in-core attr leaf header and the shortform/leaf helper APIs used by the higher-level attr state machine and da btree code.

## Key Contents

`struct xfs_attr3_icleaf_hdr` is the normalized in-core representation of both legacy and CRC-enabled attr leaf headers. It contains sibling links, magic, entry count, used bytes, widened `firstused`, hole flag, and three free-map records.

The header exposes shortform helpers, shortform verification and fork removal, leaf-to-node and leaf-to-shortform conversion, `INCOMPLETE` flag manipulation, leaf split/add/remove/lookup/getvalue/list functions, shrink/unbalance helpers, hash/order utilities, entry-size calculation, buffer read, header conversion, and owner/header checks.

## Dependencies and Risks

Callers must provide initialized `xfs_da_args`, inode, transaction, geometry, and owner context consistent with the attr fork. The key invariant is that the widened in-core `firstused` must be converted correctly for 64 KiB blocks and that callers respect the lookup convention and stateful mutation of `args` fields.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_leaf.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_remote.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_remote.c

## Purpose

`xfs_attr_remote.c` manages out-of-line extended attribute values stored in blocks mapped by the inode attr fork. It computes remote block counts, stamps and verifies CRC remote headers, reads and writes remote value buffers, finds allocation holes, steps delayed allocation, invalidates cached buffers, and removes remote extents.

## Main Behavior

Remote attr value buffers are intentionally kept out of the logging system because CRC-enabled remote blocks can require buffers larger than the maximum logged metadata buffer. CRC-enabled remote blocks reserve space for `struct xfs_attr3_rmt_hdr`; non-CRC filesystems use the whole attr block for data. `xfs_attr3_rmt_blocks` accounts for the per-block header overhead when calculating storage needs.

Read verification checks CRC, magic, uuid, physical block number, per-block byte count, offset bounds, and nonzero owner. Copy-out additionally verifies the expected owner, offset, size, and block number before copying payload data to the caller. Write paths stamp headers with magic, offset, byte count, uuid, owner, physical block number, and `NULLCOMMITLSN`, then synchronously write buffers.

`xfs_attr_rmtval_get` walks attr fork mappings, reads mapped blocks with remote buffer ops, remaps disk `-ENODATA` to `-EIO`, and copies payload out. `xfs_attr_rmt_find_hole` finds address space for a remote value, while `xfs_attr_rmtval_find_space` stores that plan in a delayed attr intent. `xfs_attr_rmtval_set_blk` allocates one mapped extent for delayed operations, and `xfs_attr_rmtval_set_value` writes the already allocated value blocks.

Removal is split between cache invalidation and extent unmapping. `xfs_attr_rmtval_invalidate` marks incore remote buffers stale before unmap, and `xfs_attr_rmtval_remove` calls `xfs_bunmapi`, returning `-EAGAIN` until all extents are removed.

## Dependencies and Risks

This file depends on bmap mapping/unmapping, attr fork geometry, buffer verification, synchronous buffer writes, delayed attr intents, health marking, and remote leaf entries from `xfs_attr_leaf.c`. Correctness depends on remote buffers never being logged, header fields matching physical storage and owner metadata, stale buffers being invalidated before reuse, and leaf entries remaining incomplete until allocation and synchronous write completion.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_remote.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_remote.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_remote.h

## Purpose

`xfs_attr_remote.h` declares the public libxfs helpers for remote extended attribute values.

## Key Contents

It exposes remote block-count calculation, a max-remote-block helper for the 64 KiB xattr size limit, value get/set helpers, stale/invalidate/remove routines, hole finding, delayed allocation setup, and per-step allocation for deferred attr intents.

## Dependencies and Risks

The declarations tie together `xfs_da_args`, `xfs_attr_intent`, inode bmap records, and buffer invalidation flags. Callers are responsible for preserving `rmtblkno`, `rmtblkcnt`, and `rmtvaluelen` consistently across delayed operation transaction rolls.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_remote.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_sf.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_sf.h

## Purpose

`xfs_attr_sf.h` defines small inline helpers and a sort record for XFS shortform extended attributes stored inside the inode attr fork.

## Key Contents

`xfs_attr_sf_sort_t` captures entry number, name length, value length, flags, hash, name pointer, and value pointer for sorting shortform attrs into hash order for listing. `XFS_ATTR_SF_ENTSIZE_MAX` reflects the maximum one-byte name/value length component.

Inline helpers compute entry sizes by lengths or by entry, find the first entry after the shortform header, advance to the next variable-length entry, and find the end pointer using the big-endian `totsize` field.

## Dependencies and Risks

The helpers assume the caller has already verified the packed shortform buffer boundaries. Miscomputed `namelen`, `valuelen`, or `totsize` would make pointer iteration unsafe, so this header is paired with the shortform verifier in `xfs_attr_leaf.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_attr_sf.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bit.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bit.c

## Purpose

`xfs_bit.c` implements small bitmap scanning helpers used by non-realtime XFS code.

## Main APIs

`xfs_bitmap_empty` scans a word array and returns 1 if every word is zero. `xfs_contig_bits` counts contiguous one bits starting at a given bit position, masking off bits before the start position and using `ffz` to find the first zero. `xfs_next_bit` finds the next set bit at or after a start position, masking off prior bits and using `ffs` to locate the set bit.

## Dependencies and Risks

The file depends on word-size constants and bit primitives from platform headers and `xfs_bit.h`. The `size` argument is a count of bitmap words, not bytes; callers must pass a valid `start_bit` for `xfs_contig_bits`, which asserts that the start is within range.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bit.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bit.h

## Purpose

`xfs_bit.h` declares XFS bitmap helpers and provides inline bit-mask and bit-position utilities.

## Key Contents

The mask helpers build high or low bit masks for 32-bit and 64-bit values. `xfs_highbit32` and `xfs_highbit64` return the highest set bit index or `-1` if the value is zero. `xfs_lowbit32` and `xfs_lowbit64` return the lowest set bit index or `-1` if none is set; the 64-bit low-bit helper checks the low word first and then the high word.

The header declares `xfs_bitmap_empty`, `xfs_contig_bits`, and `xfs_next_bit` from `xfs_bit.c`.

## Dependencies and Risks

The inline helpers depend on platform `fls`, `fls64`, and `ffs` semantics where zero returns 0. Mask helpers assume meaningful `n` values from callers; shifting by the full width or negative values would be invalid C behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bit.h -->