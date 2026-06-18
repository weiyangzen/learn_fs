# sources/distributed-fs/ceph-client/fs/ext4/extents_status.h

## Purpose

`extents_status.h` declares the public contract for ext4's in-memory extent status cache and bigalloc pending reservation tree. It defines the status bit encoding, the rb-tree node types, superblock statistics, public ES/pending APIs, and inline helpers used by mapping, delayed allocation, fiemap, shrinker, and block-freeing code.

The header is intentionally about volatile runtime state, not an on-disk structure. Its definitions let ext4 store both physical block numbers and status flags in `extent_status.es_pblk` while preserving fast inline tests for written, unwritten, delayed, hole, mapped, and referenced states.

## Important APIs, types, and macros

- Status bit layout: `ES_WRITTEN_B`, `ES_UNWRITTEN_B`, `ES_DELAYED_B`, `ES_HOLE_B`, `ES_REFERENCED_B`, `ES_FLAGS`, `ES_SHIFT`, `ES_MASK`.
- Status masks: `EXTENT_STATUS_WRITTEN`, `EXTENT_STATUS_UNWRITTEN`, `EXTENT_STATUS_DELAYED`, `EXTENT_STATUS_HOLE`, `EXTENT_STATUS_REFERENCED`, `ES_TYPE_MASK`, `ES_TYPE_VALID()`.
- Core types: `struct extent_status`, `struct ext4_es_tree`, `struct ext4_es_stats`.
- Pending reservation types: `struct pending_reservation`, `struct ext4_pending_tree`.
- ES lifecycle/mutation/query APIs: `ext4_init_es()`, `ext4_exit_es()`, `ext4_es_init_tree()`, `ext4_es_insert_extent()`, `ext4_es_cache_extent()`, `ext4_es_remove_extent()`, `ext4_es_find_extent_range()`, `ext4_es_lookup_extent()`, `ext4_es_scan_range()`, `ext4_es_scan_clu()`, `ext4_clear_inode_es()`.
- Shrinker APIs: `ext4_es_register_shrinker()`, `ext4_es_unregister_shrinker()`, `ext4_seq_es_shrinker_info_show()`.
- Pending reservation APIs: `ext4_init_pending()`, `ext4_exit_pending()`, `ext4_init_pending_tree()`, `ext4_remove_pending()`, `ext4_is_pending()`, `ext4_es_insert_delayed_extent()`.
- Inline helpers: `ext4_es_status()`, `ext4_es_type()`, `ext4_es_is_written()`, `ext4_es_is_unwritten()`, `ext4_es_is_delayed()`, `ext4_es_is_hole()`, `ext4_es_is_mapped()`, `ext4_es_set_referenced()`, `ext4_es_clear_referenced()`, `ext4_es_is_referenced()`, `ext4_es_pblock()`, `ext4_es_show_pblock()`, `ext4_es_store_pblock()`, `ext4_es_store_pblock_status()`.

## Control flow and usage model

Callers initialize one `struct ext4_es_tree` per inode and one `struct ext4_pending_tree` per inode, then use the declared APIs in `extents_status.c` to insert authoritative mapping changes, cache read-side extent discoveries, remove invalidated ranges, or query cached status. The inline helpers are used everywhere a caller needs to decode `es_pblk` or build a new status entry before insertion.

The status type bits are mutually exclusive except for `EXTENT_STATUS_REFERENCED`, which is an aging marker used by the shrinker. `ext4_es_is_mapped()` treats written and unwritten extents as mapped because both carry real physical block numbers. Delayed and hole entries use sentinel physical block values, and `ext4_es_show_pblock()` converts the all-ones non-block sentinel to zero for display/reporting.

Pending reservation declarations support bigalloc accounting. A pending reservation records a logical cluster that is shared between delayed/unwritten reservation state and already allocated written/unwritten extents. `ext4_is_pending()` and `ext4_remove_pending()` are consumed by block freeing paths, while `ext4_es_insert_delayed_extent()` is consumed by delayed allocation paths.

## State and persistence behavior

The header's structures are volatile in-memory state and are rebuilt as needed. `struct extent_status` stores a logical start, length, and packed physical/status word. `struct ext4_es_tree` stores the rb-tree root and the last-hit cache pointer. `struct ext4_es_stats` stores reclaim and lookup statistics in percpu counters plus scan timing. `struct pending_reservation` stores a logical cluster in a separate rb-tree.

The bit packing in `es_pblk` is a critical ABI-internal invariant. `ES_SHIFT` reserves the high `ES_FLAGS` bits for status flags, and `ES_MASK` is used to strip or preserve those bits. `ext4_es_store_pblock_status()` validates that only one type bit is set through `ES_TYPE_VALID(status & ES_TYPE_MASK)` before packing a status and physical block.

## Dependencies and integration points

The header depends on ext4 logical/physical block typedefs, Linux rb-tree nodes, percpu counters, `struct inode`, `struct seq_file`, and ext4 superblock/inode private types. It is included by extent mapping, delayed allocation, truncate/punch, fiemap, shrinker, and fast-commit related code. `extents.c` uses the ES APIs to cache on-disk extents, invalidate stale ranges, and coordinate bigalloc partial-cluster freeing.

## Risks and edge cases

- Physical block numbers must fit below `ES_MASK`; `extents_status.c` enforces this with `BUILD_BUG_ON(ES_SHIFT < 48)` during shrinker registration.
- Status type validity is only checked when storing status through the helper. Direct mutation of `es_pblk` could corrupt both block numbers and type flags.
- `EXTENT_STATUS_REFERENCED` is intentionally not exclusive. Code that compares full `ext4_es_status()` instead of `ext4_es_type()` can accidentally include the reference bit.
- Delayed and hole extents may not have meaningful physical blocks. Callers must use status helpers before treating `ext4_es_pblock()` as real.
- Pending reservation comments encode important bigalloc semantics; misusing the pending APIs can break delayed reservation and quota accounting even though no on-disk structure is directly modified.

## Test signals

The header itself has no executable tests, but its helpers are exercised by ES insertion/lookup/removal, shrinker aging, bigalloc pending reservation tests, and KUnit exports from `extents.c` for ES initialization, lookup, insert, shrinker registration, and related extent mapping helpers. Boundary tests should cover mutually exclusive type packing, reference-bit preservation, sentinel physical block display, mapped-vs-delayed/hole classification, and bigalloc pending tree initialization/query/remove behavior.
