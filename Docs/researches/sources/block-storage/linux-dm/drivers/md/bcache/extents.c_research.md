# File Research: sources/block-storage/linux-dm/drivers/md/bcache/extents.c

## Purpose
Implements btree key operations for both interior btree pointers and leaf data extents: validation, bad/stale filtering, formatting, overlap fixup, dirty accounting, and extent merging.

## Main Interfaces
- Text/status helpers: `bch_extent_to_text()` and internal pointer-status formatting.
- Interior pointer validation: `__bch_btree_ptr_invalid()` plus `bch_btree_keys_ops`.
- Extent validation: `__bch_extent_invalid()` plus `bch_extent_keys_ops`.
- Sort/insert/merge hooks: extent sort comparison/fixup, extent insert fixup, extent merge, and btree pointer insert fixup.

## Control Flow
Interior btree pointer operations reject null, dirty, zero-size, out-of-bucket, and stale/bad pointers, and increment `prio_blocked` for freeing keys. Extent sort fixup processes overlapping extents newest-to-oldest, trimming or splitting older keys so in-memory leaf nodes do not contain overlap. Extent insert fixup walks existing overlapping keys, validates optional replace semantics, adjusts dirty sector accounting, splits middle overlaps, trims old extents, and finally accounts inserted dirty sectors. Merge hooks combine adjacent extents only when headers, pointer continuity, bucket containment, and checksum rules allow it.

## State And Synchronization
Validation can inspect bucket state under `bucket_lock` for expensive debug checks. Dirty accounting updates per-device dirty sector tracking through writeback helpers. Normal callers hold btree locks through bset/btree insertion paths.

## Integration Points
Provides `btree_keys_ops` used by `btree.c` and `bset.c`: `bch_btree_keys_ops` for interior nodes and `bch_extent_keys_ops` for leaf extents. Uses `writeback.h`, bucket helpers, debug macros, and cache-set error reporting.

## Notable Behaviors
- Pointer status distinguishes invalid physical ranges, stale generations, null keys, no pointers, and zeroed keys.
- Stale dirty pointers are logged before being treated as bad.
- Extent merging can merge checksum state, drop checksums when only one side has one, or cap size at `USHRT_MAX`.
- Replace insertion acts like compare-and-swap and can shrink the inserted key to the verified covered portion.

## Risks And Review Focus
- Overlap trimming and dirty-sector accounting must stay in sync to avoid leaked or negative dirty accounting.
- Replace-key validation depends on exact pointer arithmetic including generation bits.
- Expensive debug checks catch bucket mark/priority inconsistencies that would otherwise indicate serious GC corruption.
