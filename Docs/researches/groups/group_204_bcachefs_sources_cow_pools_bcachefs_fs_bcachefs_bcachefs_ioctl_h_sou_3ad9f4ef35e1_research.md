# Group Research: group_204_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_bcachefs_ioctl_h_sou_3ad9f4ef35e1

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs_ioctl.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs_ioctl.h

This header defines the bcachefs user/kernel ioctl ABI. It is a stable interface surface for filesystem-wide operations, device management, fsck, accounting queries, subvolume/snapshot queries, and several file-specific recovery operations.

Key contents:
- Common force flags: `BCH_FORCE_IF_*`, plus device addressing flags `BCH_BY_INDEX` and `BCH_READ_DEV`.
- Filesystem ioctls under ioctl type `0xbc`, including disk add/remove/online/offline, state changes, resizing, journal resizing, data operations, superblock reads, subvolume operations, fsck, accounting/counters, subvolume listing/path resolution, and snapshot-tree queries.
- Versioned ABI structs such as `bch_ioctl_disk_v2`, `bch_ioctl_disk_set_state_v2`, `bch_ioctl_disk_resize_v2`, and `bch_ioctl_subvolume_v2` add `bch_ioctl_err_msg` for detailed userspace error reporting.
- Background data operations use `struct bch_ioctl_data`, `bch_ioctl_data_event`, and `bch_ioctl_data_progress` to expose progress for scrub/rereplicate/migrate/rewrite/drop-extra-replicas jobs through a returned file descriptor.
- Obsolete usage structs remain present for compatibility: `bch_ioctl_fs_usage`, `bch_ioctl_dev_usage`, and `bch_ioctl_dev_usage_v2`.
- Newer metadata query structures expose disk accounting (`bch_ioctl_query_accounting`), counters, subvolume directory entries, subvolume-to-path resolution, and full snapshot tree nodes with per-snapshot accounting.
- File-specific ioctls include raw direct reads with extended error reporting (`BCHFS_IOC_PREAD_RAW`) and unpoisoning poisoned file extents (`BCHFS_IOC_UNPOISON`).

Important details:
- Many structs use fixed-width integer types and explicit padding because they define ABI layout.
- Several flexible-array structs carry user buffers or variable entries; callers must respect input/output size semantics such as `-ERANGE`.
- `bch_ioctl_subvol_dirent_path_len()` computes a bounded path length using `reclen`, preserving safety around padded variable-length records.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bbpos.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bbpos.h

This small header provides helpers for `struct bbpos`, a combined btree-id plus btree-position cursor.

Key contents:
- `bbpos_cmp()` orders first by btree id, then by `bpos`.
- `bbpos_successor()` advances within the current btree until `SPOS_MAX`, then advances to the next btree and resets position to `POS_MIN`; it BUGs if advanced beyond `BTREE_ID_NR`.
- `bch2_bbpos_to_text()` renders a combined position as `<btree-name>:<bpos>`.

Role:
- Used by cache pinning and GC generation progress tracking where a global position must span multiple btrees, not only positions inside one tree.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bbpos.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bbpos_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bbpos_types.h

This header defines the `bbpos` data type.

Key contents:
- `struct bbpos` contains `enum btree_id btree` and `struct bpos pos`.
- `BBPOS()` constructs a value.
- `BBPOS_MIN` starts at btree 0 and `POS_MIN`.
- `BBPOS_MAX` ends at `BTREE_ID_NR - 1` and `SPOS_MAX`.

Role:
- Provides a compact cross-btree cursor type for code that needs monotonic ordering across btree spaces, especially GC and cache pinning ranges.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bbpos_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey.c

This file implements packed bkey format handling: packing, unpacking, lossy position packing, format construction/validation, byte swapping, packed comparisons, and optional compiled-unpack support.

Key contents:
- `bch2_bkey_format_current` defines the current unpacked key format.
- Packing/unpacking is built around `pack_state` and `unpack_state`, with `get_inc_field()`, `set_inc_field()`, and `set_inc_field_lossy()`.
- `bch2_bkey_transform()` converts a packed key/value from one packed format to another.
- `__bch2_bkey_unpack_key()` and `__bch2_bkey_unpack_key_b()` unpack packed keys; the latter has a little-endian fast path using precomputed byte-aligned load constants from `bch2_compute_bkey_unpack_consts()`.
- `bch2_bkey_pack_key()` and `bch2_bkey_pack()` pack key-only and key-plus-value forms.
- `bch2_bkey_pack_pos_lossy()` creates a packed search position that is exact, smaller than the requested position, or impossible; bset lookup relies on this to search auxiliary trees efficiently.
- `bch2_bkey_format_init()`, `bch2_bkey_format_add_pos()`, and `bch2_bkey_format_done()` derive compact local formats from observed key ranges.
- `bch2_bkey_format_invalid()` validates packed format metadata against current field widths and computed `key_u64s`.
- `bch2_bkey_greatest_differing_bit()` and `bch2_bkey_ffs()` support auxiliary search tree compression.
- The disabled `HAVE_BCACHEFS_COMPILED_UNPACK` block contains x86 instruction emission for runtime unpack functions.
- `bch2_bpos_swab()` and `bch2_bkey_swab_key()` handle endian conversion of positions/keys.

Important invariants:
- Packed keys use per-field offsets plus bit widths and must not represent values larger than the unpacked format.
- Extent start-position invariants are explicitly not preserved by the generic transform helper.
- Debug branches verify pack/unpack equivalence and packed comparison correctness.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey.h

This header is the main inline API for bkey and bpos manipulation, packed/unpacked conversions, comparison, packing/unpacking declarations, format accounting, and byte-order helpers.

Key contents:
- Copy helpers: `bkey_p_copy()`, `bkey_copy()`, and `bkey_val_copy()`.
- `bpos_*` comparison helpers compare inode, offset, and snapshot; `bkey_*` comparison helpers compare only inode and offset.
- Version helpers define `ZERO_VERSION`, `MAX_VERSION`, `bversion_cmp()`, and `bversion_eq()`.
- Packed/unpacked detection and casts: `bkey_packed()`, `bkey_to_packed()`, `packed_to_bkey()`, and const variants.
- Position navigation helpers: `bpos_successor()`, `bpos_predecessor()`, no-snapshot variants, `bkey_start_offset()`, and `bkey_start_pos()`.
- Packed-key sizing helpers: `bkeyp_key_u64s()`, `bkeyp_val_u64s()`, `bkeyp_val_bytes()`, and `bkeyp_val()`.
- Public declarations for transform, pack/unpack, lossy position packing, format validation, and format rendering.
- `__bkey_unpack_key_format_checked()` chooses compiled unpack support if enabled, otherwise the normal fast path, with optional debug verification.
- `bkey_disassemble()` and `__bkey_disassemble()` split a packed key into an unpacked key pointer plus value pointer.
- Byte-order macros define `high_word()`, `next_word()`, `prev_word()`, and `high_bit_offset`.
- `bkey_fields()` centralizes the six packable fields: inode, offset, snapshot, size, version high, and version low.

Role:
- This is the hot inline layer used by bset lookup, btree iteration, validation, and mutation paths. It encodes the difference between full key identity including snapshot and extent/range comparisons using only inode/offset.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_buf.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_buf.h

This header defines a small reusable buffer for assembling, copying, and unpacking bkeys.

Key contents:
- `struct bkey_buf` contains a `struct bkey_i *k` plus a 12-u64 inline stack buffer.
- `bch2_bkey_buf_init()` points `k` at the inline buffer and initializes the key.
- `bch2_bkey_buf_realloc_noprof()` switches from inline storage to a 2048-byte heap allocation when requested u64 count exceeds the inline capacity.
- `bch2_bkey_buf_reassemble_noprof()` copies a split const key/value into inline/heap `bkey_i` storage.
- `bch2_bkey_buf_copy_noprof()` copies a full inline bkey.
- `bch2_bkey_buf_unpack_noprof()` unpacks a packed key from a btree node into the buffer.
- `bch2_bkey_buf_exit()` frees heap storage if used.

Role:
- Used in traversal/repair/cache paths that need a stable `bkey_i` copy while iterators, journal overlays, or cache lookups may move independently.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_cmp.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_cmp.h

This header implements hot packed-key comparison helpers.

Key contents:
- `__bkey_cmp_bits()` compares the packed key bitstream across the configured number of key bits.
- On x86-64, it uses inline assembly to compare descending packed words efficiently.
- The generic path masks off header bits, advances through words with `next_word()`, and returns `cmp_int()` of the first differing word.
- `__bch2_bkey_cmp_packed_format_checked_inlined()` compares two packed keys in the same btree format and debug-checks equivalence against unpacked `bpos` comparison.
- `bch2_bkey_cmp_packed_inlined()` handles mixed packed/unpacked inputs by unpacking the packed side when necessary, otherwise directly comparing `bpos`.

Role:
- This is a performance-critical comparator for bset auxiliary tree lookup and btree-node iteration ordering.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_cmp.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_methods.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_methods.c

This file defines per-key-type operations, generic bkey validation, text rendering, merging, type compatibility translation, and old-format migration.

Key contents:
- `bch2_bkey_types[]` maps key type ids to names.
- Basic ops are defined for deleted, whiteout, extent whiteout, error, cookie, hash whiteout, inline data, and set keys.
- `bch2_bkey_ops[]` is generated from `BCH_BKEY_TYPES()` and dispatches validation, rendering, swabbing, merge, trigger, and compatibility operations.
- `bch2_set_bkey_error()` converts a key to `KEY_TYPE_error`, using the extended key-type-error feature when available.
- `bch2_bkey_val_validate()` checks minimum value size and invokes type-specific validation.
- `__bch2_bkey_validate()` performs generic structural checks: key u64 count, allowed key type for btree/node type, extent size rules, snapshot field rules, and `POS_MAX` exclusion.
- `bch2_bpos_to_text()`, `bch2_bkey_to_text()`, `bch2_val_to_text()`, and `bch2_bkey_val_to_text()` provide common diagnostic rendering.
- `bch2_bkey_merge()` checks mergeability and calls the type-specific merge function when enabled.
- `bch2_bkey_renumber()` maps pre-renumbering key type ids to current ids for old metadata.
- `__bch2_bkey_compat()` performs read/write compatibility transforms: endian swab, type renumbering, old inode btree field swap, old snapshot encoding, value swab, and type-specific compatibility.

Important interactions:
- Validation is sensitive to `BCH_FS_no_invalid_checks`.
- Strict key-type enforcement depends on commit context, internal btree nodes, and key type flags.
- Compatibility transformations run in reverse order on write.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_methods.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_methods.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_methods.h

This header declares the bkey operation table and helpers for validation, rendering, merging, triggers, and metadata compatibility.

Key contents:
- `struct bkey_ops` contains callbacks for `key_validate`, `val_to_text`, `swab`, `key_merge`, `trigger`, and `compat`, plus `min_val_size`.
- `bch2_bkey_type_ops()` safely maps a key type to its operations or null ops.
- Validation/rendering declarations cover whole key validation, value validation, bpos/bkey text, and key-value text.
- `bch2_bkey_maybe_mergable()` checks same type, same version, and contiguous positions.
- `bch2_key_trigger()`, `bch2_key_trigger_old()`, and `bch2_key_trigger_new()` wrap trigger calls for overwrite/delete/insert cases using synthetic deleted keys.
- Compatibility and error helpers are declared: `bch2_bkey_renumber()`, `bch2_bkey_compat()`, and `bch2_set_bkey_error()`.

Role:
- This is the shared interface between generic btree code and individual bkey value-type implementations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_methods.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_types.h

This header defines the basic bkey wrapper model and generates typed wrappers for every bcachefs key value type.

Key contents:
- Documentation explains `struct bpos` as the sortable search key and `struct bkey` as the key header containing u64 count, format, type, version, extent size, and position.
- `bkey_next()`, `bkey_val_u64s()`, `bkey_val_bytes()`, `set_bkey_val_u64s()`, and `set_bkey_val_bytes()` operate on inline key/value sizes.
- Whiteout/deleted helpers distinguish deleted, whiteout, and extent-whiteout key states.
- `struct bkey_s_c` and `struct bkey_s` represent split key/value views, const and mutable.
- Generic conversion helpers create split views from `bkey` and `bkey_i`.
- The `BCH_BKEY_TYPES()` macro expansion generates, for each value type:
  - `bkey_i_<name>` inline key/value type.
  - `bkey_s_<name>` and `bkey_s_c_<name>` split typed views.
  - Conversion helpers that BUG if the runtime key type does not match.
  - Initialization helpers that zero the typed value and set type/value length.
- `enum bch_validate_flags` and `struct bkey_validate_context` define validation context, including source, flags, level, btree id, root flag, and journal location.

Role:
- This file is the type-safe bridge between generic btree storage and individual on-disk value structs such as extents, inodes, dirents, xattrs, allocation keys, and snapshot/subvolume records.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bset.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bset.c

This file implements sorted key sets inside btree nodes, auxiliary search trees, btree-node iterators, insertion/deletion within the current bset, lookup, stats, and debug rendering.

Key contents:
- Extensive documentation explains read-write bsets, read-only bsets, and auxiliary search trees.
- Text/debug helpers render btree node keys, individual bsets, and iterators.
- Key counting and verification keep `struct btree_nr_keys` consistent with actual non-deleted keys.
- Auxiliary tree implementation:
  - Read-only bsets use Eytzinger-layout array search trees with compact `struct bkey_float` nodes containing exponent, key offset, and mantissa.
  - Writable bsets use a cheaper `struct rw_aux_tree` table with one sampled key per cacheline-ish region.
  - Builders `__build_ro_aux_tree()` and `__build_rw_aux_tree()` allocate/search structures in `b->aux_data`.
  - Verification helpers check aux tree layout, offsets, and consistency.
- Bset initialization: `bch2_btree_keys_init()`, `bch2_bset_init_first()`, and `bch2_bset_init_next()`.
- Predecessor lookup uses aux structures to find a nearby previous key, then linearly scans.
- Insert/delete:
  - `bch2_bset_insert()` packs inserted keys when possible, shifts storage, writes key/value, updates bset size, lookup table, and key accounting.
  - `bch2_bset_delete()` removes clobbered u64s and fixes lookup tables.
- Lookup:
  - `bch2_btree_node_iter_init()` searches each bset using a lossy packed search key when possible, then linear-searches to the exact iterator start.
  - Fallback handles positions that cannot be packed.
- Iterator logic merges up to `MAX_BSETS` sorted bsets using compact offset pairs, with sorted advance, previous-key support, and deleted-key filtering.
- `bch2_btree_keys_stats()` reports set types, bytes, float count, and failed compressed-key nodes.
- `bch2_bfloat_to_text()` prints auxiliary-tree compression failures.

Important invariants:
- Deleted duplicate keys are sorted before the live key for equal non-extent keys; extent lookup has special semantics around equal positions.
- Auxiliary tree nodes may fail compressed comparison and fall back to real-key comparison.
- Debug branches aggressively verify sorted order, insert positions, lookup tables, and accounting.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bset.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bset.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bset.h

This header declares and inlines the bset and btree-node iterator API.

Key contents:
- Documentation explains bkeys, bsets, btree-node iterators, and auxiliary search tree compression.
- `enum bset_aux_tree_type` distinguishes no aux tree, read-only aux tree, and read-write aux tree.
- `BSET_CACHELINE` is set to 256 bytes for lookup sampling granularity.
- Aux-data sizing helpers compute cachelines and auxiliary data bytes/u64s from btree node byte order.
- Iteration macros include `for_each_bset`, `for_each_bset_c`, and `bset_tree_for_each_key`.
- `bset_aux_tree_type()`, `bset_has_ro_aux_tree()`, `bset_has_rw_aux_tree()`, and `bch2_bset_set_no_aux_tree()` manage aux-tree state.
- `btree_node_set_format()` updates the node format, computes key bits/unpack constants, compiles an unpack function if enabled, and resets aux trees.
- Bset lifecycle and mutation declarations cover initialization, aux tree building, insert, and delete.
- `bkey_cmp_p_or_unp()` compares a left packed/unpacked key to a right packed key or unpacked position.
- `bch2_bkey_to_bset_inlined()` maps a key pointer to its containing bset via node offsets.
- Iterator declarations and inline helpers expose init, push, sort, advance, peek, previous, and unpacked-peek operations.
- `bkey_iter_cmp()` defines iterator ordering, including deleted-key tie-breaking.
- Accounting helpers maintain live u64s, per-bset u64s, and packed/unpacked key counts.
- Debug declarations expose node-key rendering, bset rendering, iterator dumping, accounting verification, and iterator verification.

Role:
- This is the hot inline companion to `bset.c`; most btree traversal code depends on these iterator and comparison helpers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/bset.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/cache.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/cache.c

This file implements the in-memory btree node cache: allocation, buffer ownership, hash lookup, state transitions, pinning, reclaim/shrinker integration, cannibalization under memory pressure, node read/fill, eviction, initialization/exit, evicted-size tracking, and diagnostics.

Key contents:
- Top-level documentation defines the cache model: nodes are hashed by physical btree pointer, roots are pinned, non-roots may be evicted/reused, and callers must verify identity after locking.
- Cache states are `NONE`, `FREED`, `FREEABLE`, `CLEAN`, and `DIRTY`, managed by `bch2_btree_node_transition_state_locked()` / `bch2_btree_node_transition_state()`.
- Memory allocation:
  - Data and auxiliary buffers are allocated separately.
  - Allocation avoids compaction when configured and falls back between vmalloc/kmalloc/kvmalloc.
  - Node shells preserve locks and may move through freed/freeable/live lists.
- Pinning:
  - `bch2_node_pin()` and `bch2_btree_cache_unpin()` move nodes between normal and pinned live lists according to `bbpos` ranges and btree masks.
- Dirty/write-state handling:
  - `bch2_btree_node_set_dirty()` marks nodes dirty and moves hashed nodes to dirty lists.
  - `bch2_btree_node_write_done_clean()` settles clean/dirty state after writes.
- Key update:
  - `bch2_btree_node_update_key_early()` temporarily unhashes and rehashes a cached node when its pointer key changes.
- Reclaim:
  - Shrinker scan/count functions reclaim freeable and clean nodes while respecting reserve, permanent/noevict/write-blocked/reachable/dirty/in-flight constraints.
  - `btree_node_reclaim()` obtains intent/write locks before removing nodes from live state.
- Cannibalization:
  - `bch2_btree_cache_cannibalize_lock()` serializes emergency reclaim.
  - `btree_node_cannibalize()` can reclaim clean or dirty nodes; dirty nodes are written and waited on before reuse.
- Lookup/fill:
  - `bch2_btree_node_mem_alloc()` obtains reusable or fresh node memory, possibly unlocking/relocking transactions.
  - `bch2_btree_node_fill()` allocates a node, hashes it, starts read IO, and handles races where another fill inserted the same node.
  - `bch2_btree_node_get()` and `bch2_btree_node_get_noiter()` find, lock, validate, prefetch, and return nodes.
  - `bch2_btree_node_prefetch()` starts asynchronous read/fill when absent.
- Eviction:
  - `bch2_btree_node_evict()` waits for IO, writes dirty nodes if necessary, and transitions clean nodes to freed.
- Init/exit:
  - `bch2_fs_btree_cache_init_early()`, `bch2_fs_btree_cache_init()`, and `bch2_fs_btree_cache_exit()` manage locks, lists, hash table, reserves, shrinkers, and teardown diagnostics.
- Diagnostics render btree ids, positions, nodes, and cache accounting.

Important invariants:
- Hash transitions require write lock unless both old and new states are live hashed states.
- Dirty flags are meaningful only for hashed live states.
- Permanent nodes must never be evicted.
- After any lookup and lock, `hash_val`, btree id, level, and node header are rechecked because cached nodes may be reused.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/cache.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/cache.h

This header exposes the btree node cache API and core inline helpers.

Key contents:
- Declarations cover reserve recalculation, node memory/data free, cache-state transitions, pin/unpin, dirty/write completion, early key update, cannibalize lock/unlock, memory allocation, node get/get_noiter/prefetch/evict, cache init/exit, and evicted-size table lifecycle.
- `btree_evicted_size_pack()`, `bch2_btree_evicted_size_record()`, and `bch2_btree_evicted_size_lookup()` maintain a compact hash-indexed record of recently evicted node live-u64 counts.
- `btree_ptr_hash_val()` derives the cache key from `KEY_TYPE_btree_ptr` start pointer or `KEY_TYPE_btree_ptr_v2` sequence.
- `btree_node_mem_ptr()` extracts the optional in-memory pointer optimization from v2 btree pointers.
- `btree_node_hashed()` and `btree_node_live_state()` classify node state from hash value and dirty/write-in-flight flags.
- `for_each_cached_btree` iterates the rhashtable under RCU.
- Size helpers compute btree buffer bytes, max key u64s, sectors, and blocks.
- Split/merge thresholds are derived from max node u64s.
- Root helpers map btree id to root, including dynamic extra roots.
- `btree_node_is_root()` verifies a node against its root and checks level consistency.
- Text rendering declarations cover btree ids, positions, nodes, and cache stats.
- `trace_btree_node()` standardizes trace rendering of node positions.

Role:
- This is the shared interface used by btree traversal, read/write, topology repair, and diagnostics to work with cached btree nodes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/cache.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/check.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/check.c

This file implements btree topology repair, allocation/reference checking, GC marking, stale pointer generation cleanup, btree-node merging, and GC initialization.

Key contents:
- `bch2_gc_pos_to_text()` renders current GC phase and btree position.
- Topology repair:
  - `btree_ptr_to_v2()` normalizes old btree pointers to v2 form.
  - `set_node_min()` and `set_node_max()` update node boundary metadata, journal replacement keys, drop out-of-range keys, and rehash nodes when max key changes.
  - `btree_check_node_boundaries()` detects gaps/overlaps between sibling child nodes and decides whether to adjust min/max, drop overwritten nodes, or fill from scanned nodes.
  - `btree_check_root_boundaries()` ensures roots span `POS_MIN` to `SPOS_MAX`.
  - `btree_repair_node_end()` fixes a final child whose max does not reach the parent key.
  - `bch2_btree_repair_topology_recurse()` walks child pointers, handles unreadable/stale nodes, deletes invalid journal keys, repairs boundaries, recurses into children, and drops empty interior nodes.
  - `bch2_topology_check_root()` reconstructs unreadable roots from scans or fake roots depending on btree capabilities.
  - `bch2_check_topology()` runs topology checks for all live btrees during recovery and resets read-error ratelimiters afterward.
- GC marking/allocation checking:
  - `bch2_gc_mark_key()` validates topology at node changes, checks future key versions, ensures btree pointer allocation bitmap marking, runs check-repair triggers, commits required repair updates, then runs GC insert triggers.
  - `bch2_gc_btree_root()`, `bch2_gc_btree()`, and `bch2_gc_btrees()` walk all btrees in GC order and mark references.
  - `bch2_mark_superblocks()` marks superblock references.
  - `bch2_gc_start()`, `bch2_gc_alloc_start()`, and `bch2_gc_free()` allocate/free temporary GC state.
  - `bch2_alloc_write_key()` compares allocation btree keys with GC-recomputed bucket state and repairs data type, generation, dirty sectors, stripe sectors, cached sectors, and stripe refcount.
  - `bch2_gc_alloc_done()` applies allocation repairs across member devices.
  - `bch2_gc_write_stripes_key()` repairs erasure-coded stripe block sector counts and clears parity block counts.
  - `bch2_check_allocations()` orchestrates full reference checking: flush interior updates, start accounting/dev/reflink/alloc GC state, mark superblocks, walk btrees, repair alloc/accounting/stripes/reflink, clear GC state, wake allocators, and clean deleted member records.
- Generation cleanup:
  - `bch2_gc_gens()` snapshots oldest bucket generations, walks data-pointer btrees to drop stale ptrs, writes oldest generations back to alloc keys, updates the superblock `no_stale_ptrs` compat bit, and frees temporary arrays.
  - `bch2_gc_gens_async()` queues async generation cleanup under a write reference.
- Btree merge pass:
  - `merge_btree_node_one()` checks whether a node needs merging and calls foreground merge when appropriate.
  - `bch2_merge_btree_nodes()` scans every live btree and level, merging underfull nodes and logging merge counts.
- `bch2_fs_btree_gc_init_early()` initializes GC position seqcount, async work, GC lock, and generation lock.

Important invariants:
- Topology repair runs during mount/recovery and relies on old nofail lock assumptions because no worker contention should exist yet.
- GC trigger execution is carefully split because some trigger modes are not idempotent across transaction restarts.
- GC traversal order matters to avoid missing references that move during index updates.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/btree/check.c -->