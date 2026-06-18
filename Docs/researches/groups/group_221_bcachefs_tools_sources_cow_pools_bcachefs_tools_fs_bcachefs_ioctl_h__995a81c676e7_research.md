# Group Research: group_221_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_bcachefs_ioctl_h__995a81c676e7

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/bcachefs-tools`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/bcachefs_ioctl.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/bcachefs_ioctl.h

## Purpose
Defines the bcachefs userspace/kernel ioctl ABI for filesystem-wide and file-specific operations. This is a public contract header: layout, ioctl numbers, packing, alignment, and pointer-width decisions matter for compatibility.

## Main Contents
- Common force flags:
  - `BCH_FORCE_IF_DATA_LOST`
  - `BCH_FORCE_IF_METADATA_LOST`
  - `BCH_FORCE_IF_DATA_DEGRADED`
  - `BCH_FORCE_IF_METADATA_DEGRADED`
  - aggregate `BCH_FORCE_IF_LOST` and `BCH_FORCE_IF_DEGRADED`
- Device-addressing flags:
  - `BCH_BY_INDEX`: interpret `dev` as filesystem device index instead of pathname pointer.
  - `BCH_READ_DEV`: read a specific device superblock.
- Filesystem ioctl command definitions for:
  - UUID query
  - disk add/remove/online/offline/state/resize/journal resize
  - data jobs
  - usage/accounting/counters
  - superblock read
  - subvolume create/destroy/list/path
  - snapshot tree query
  - offline/online fsck
- File-specific ioctl command definitions for:
  - reinheriting attrs
  - reflink option propagation controls
  - raw pread with extended errors
  - unpoisoning file ranges

## ABI Structures
- `struct bch_ioctl_err_msg` is a reusable user-buffer error-reporting descriptor used by v2 ioctls.
- Device operation structures exist in legacy and v2 forms, where v2 variants append `err`.
- `struct bch_ioctl_data` starts background data jobs such as scrub, rereplicate, migrate, rewrite old nodes, and drop extra replicas. It carries btree ranges and operation-specific parameters.
- `struct bch_ioctl_data_event` reports progress from the returned job fd, currently with progress events only.
- `struct bch_replicas_usage`, `bch_ioctl_fs_usage`, `bch_ioctl_dev_usage`, and `bch_ioctl_dev_usage_v2` support older usage-query interfaces.
- `struct bch_ioctl_query_accounting` returns `bkey_i_accounting` entries.
- `struct bch_ioctl_query_counters` returns variable-length counter data.
- Subvolume ABI:
  - `bch_ioctl_subvol_dirent`
  - `bch_ioctl_subvol_readdir`
  - `bch_ioctl_subvol_to_path`
  - `bch_ioctl_snapshot_node`
  - `bch_ioctl_snapshot_tree_query`
- Raw recovery ABI:
  - `bch_ioctl_pread_raw` reports checksum, IO, decompression, and erasure-code reconstruction errors.
  - `bch_ioctl_unpoison` clears poison state over a file range.

## Notable Details
- Many user pointers are represented as `__u64`, keeping the ABI explicit across user/kernel boundary.
- Several variable-length arrays appear at the end of ioctl structures: `replicas[]`, `d[]`, `devs[]`, `accounting[]`, `nodes[]`.
- Some structs are explicitly `__packed __aligned(8)` to preserve expected userspace layout.
- `bch_ioctl_subvol_dirent_path_len()` treats `reclen` as an 8-byte-aligned record length with a NUL-terminated path inside it.
- Legacy and replacement ioctls coexist; comments mark old usage interfaces obsolete.

## Risks / Review Notes
- Ioctl numbers are ABI-sensitive. `BCH_IOCTL_FS_USAGE` and `BCH_IOCTL_DEV_USAGE` both use command number `11` with different structs, and `BCH_IOCTL_QUERY_ACCOUNTING` and `BCH_IOCTL_QUERY_COUNTERS` both use command number `21`; callers must rely on the intended dispatch context or compatibility handling.
- Typo-level comments exist, e.g. “offline or offline” and “approprate”; no code effect.
- The `__counted_by()` comment in `bch_ioctl_fsck_offline` documents an intentional avoidance of a compiler bounds-check issue for userspace pointers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/bcachefs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bbpos.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bbpos.h

## Purpose
Provides helpers for `struct bbpos`, a combined btree-id plus btree-position cursor.

## Main Functions
- `bbpos_cmp(l, r)`: orders first by `btree`, then by `bpos_cmp()`.
- `bbpos_successor(pos)`: advances within the current btree position until `SPOS_MAX`, then moves to the next btree and resets position to `POS_MIN`.
- `bch2_bbpos_to_text(out, pos)`: prints `btree_id:bpos`.

## Dependencies
- `bbpos_types.h` for `struct bbpos`.
- `bkey_methods.h` for `bch2_bpos_to_text()`.
- `cache.h` for `bch2_btree_id_to_text()`.

## Notable Details
- `bbpos_successor()` uses `BUG()` if it cannot advance.
- The successor logic can produce a one-past-known btree id when called at the last btree’s `SPOS_MAX`, because it checks `pos.btree != BTREE_ID_NR` before incrementing. That may be intentional sentinel behavior, but callers must not assume the result is always within `0..BTREE_ID_NR - 1`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bbpos.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bbpos_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bbpos_types.h

## Purpose
Defines the compact type used to identify an ordered position across all btrees.

## Main Contents
- `struct bbpos`:
  - `enum btree_id btree`
  - `struct bpos pos`
- `BBPOS(btree, pos)` inline constructor.
- Boundary macros:
  - `BBPOS_MIN`: btree `0`, `POS_MIN`
  - `BBPOS_MAX`: btree `BTREE_ID_NR - 1`, `SPOS_MAX`

## Role In System
Used by btree-cache pinning and any logic that needs an ordered global cursor over `(btree id, key position)`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bbpos_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey.c

## Purpose
Implements bcachefs bkey packing, unpacking, packed-position comparison support, packed-format synthesis/validation, endian swapping, and optional compiled unpack code.

## Main Areas
- `bch2_bkey_format_current`: current unpacked bkey format.
- Binary/text rendering:
  - `bch2_bkey_packed_to_binary_text()`
  - `bch2_bkey_format_to_text()`
- Packing/unpacking state machines:
  - `pack_state`
  - `unpack_state`
  - `get_inc_field()`
  - `set_inc_field()`
  - `set_inc_field_lossy()`
- Full key transform/pack/unpack:
  - `bch2_bkey_transform()`
  - `__bch2_bkey_unpack_key()`
  - `__bch2_bkey_unpack_key_b()`
  - `bch2_bkey_pack_key()`
  - `bch2_bkey_unpack()`
- Position-only packing:
  - `bch2_bkey_pack_pos()`
  - `bch2_bkey_pack_pos_lossy()`
- Packed-format construction:
  - `bch2_bkey_format_init()`
  - `bch2_bkey_format_add_pos()`
  - `bch2_bkey_format_done()`
  - `bch2_bkey_format_invalid()`
- Packed comparison support:
  - `bch2_bkey_greatest_differing_bit()`
  - `bch2_bkey_ffs()`
  - `bch2_bkey_cmp_packed()`
  - `__bch2_bkey_cmp_left_packed()`
- Byte-order conversion:
  - `bch2_bpos_swab()`
  - `bch2_bkey_swab_key()`

## Fast Paths
- Little-endian byte-aligned formats get precomputed per-field constants in `bch2_compute_bkey_unpack_consts()`.
- `pack_field_fast()` and `unpack_field_fast()` use unaligned 8-byte loads/stores around precomputed byte windows.
- `__bch2_bkey_unpack_key_b()` uses a header trick: a 4-byte unaligned load starting one byte before the packed key, then shifts/adds to construct the unpacked header.
- `__bkey_unpack_pos_b()` avoids full key unpacking for lookup hot paths.
- Exact and lossy position packing both have byte-aligned fast paths.

## Lossy Position Packing
`bch2_bkey_pack_pos_lossy()` packs a search position into the local btree format. If exact packing is impossible:
- field underflow rolls the lower field up by decrementing the higher field and saturating lower fields,
- field overflow clamps the overflowing field and saturates lower fields,
- the result is the greatest representable packed position still less than or equal to the original search key,
- inode underflow fails.

This behavior is used by bset lookup, where a packed approximate key can safely guide auxiliary-tree comparison as long as it is not greater than the real search position.

## Format Generation
`bch2_bkey_format_done()` computes per-field bit widths and offsets from observed min/max values, then rounds fields to byte widths when spare bits permit. That directly enables the fast byte-aligned unpack/pack paths.

## Validation And Debugging
- Debug mode can re-unpack packed keys and compare against expected unpacked keys.
- Format validation rejects field ranges that can represent values outside the current unpacked format.
- `bch2_bkey_pack_test()` exists under debug to sanity-check pack/unpack machinery.

## Optional Compiled Unpack
There is an `#ifdef HAVE_BCACHEFS_COMPILED_UNPACK` implementation that emits x86-64 machine code for unpacking. The header currently disables the feature with `#if 0`, so the normal build path uses C fast paths.

## Risks / Review Notes
- Many helpers rely on carefully controlled unaligned reads, leading padding, and no overflow/carry assumptions. The padded stack wrapper types in `bkey.h` are important when using packed keys outside a bset.
- Big-endian support falls back for several byte-aligned fast paths; performance and coverage differ by endian.
- The compiled-unpack code is dormant but still present; if re-enabled, executable-memory allocation and instruction emission need separate scrutiny.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey.h

## Purpose
Primary public helper header for bkey comparison, packing/unpacking declarations, position arithmetic, bversion comparison, and packed/unpacked key utilities.

## Main Contents
- Copy helpers:
  - `bkey_p_copy()`
  - `bkey_copy()`
  - `bkey_val_copy()`
- Position comparison helpers:
  - `bpos_eq/lt/le/gt/ge/cmp`
  - `bkey_eq/lt/le/gt/ge/cmp`, ignoring snapshot
  - min/max helpers
- Version helpers:
  - `bversion_cmp()`
  - `bversion_eq()`
  - `ZERO_VERSION`
  - `MAX_VERSION`
- Packed/unpacked helpers:
  - `bkey_packed()`
  - `bkey_to_packed()`
  - `packed_to_bkey()`
  - `bkeyp_key_u64s()`
  - `bkeyp_val_u64s()`
  - `bkeyp_val()`
- Position arithmetic:
  - `bpos_successor()`
  - `bpos_predecessor()`
  - no-snapshot successor/predecessor variants
  - `bkey_start_offset()`
  - `bkey_start_pos()`
  - `bpos_with_snapshot()`
- Unpack wrappers:
  - `__bkey_unpack_key_format_checked()`
  - `bkey_unpack_key()`
  - `bkey_unpack_pos()`
  - `bkey_disassemble()`
- Format state:
  - `struct bkey_format_state`
  - `bch2_bkey_format_add_key()`
  - `bch2_bkey_format_field_overflows()`

## Important Types
- `struct bkey_packed_padded` and `struct bkey_i_padded` provide leading padding for stack-local packed keys. This is required because fast unpack paths may read bytes before the packed key address.
- `enum bkey_pack_pos_ret` distinguishes exact pack, smaller/lossy pack, and pack failure.

## Notable Details
- `bkey_cmp()` ignores `snapshot`, while `bpos_cmp()` includes it. This distinction is fundamental to lookup/extent behavior.
- `bkey_packed()` treats `KEY_FORMAT_CURRENT` as unpacked and other formats as packed.
- Endian helpers define `high_word()`, `next_word()`, and `prev_word()` differently for little vs big endian.
- Compiled unpack hooks are declared but disabled by the top-level `#if 0`.

## Risks / Review Notes
- The difference between `bpos_*` and `bkey_*` comparisons is easy to misuse.
- `bpos_successor()` and predecessor helpers `BUG()` on overflow/underflow rather than returning failure.
- Stack-local packed keys should use the padded wrappers when passed to fast unpack/compare paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_buf.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey_buf.h

## Purpose
Provides a small reusable buffer abstraction for temporary bkeys, with inline stack storage and heap fallback.

## Main Contents
- `struct bkey_buf`:
  - `struct bkey_i *k`
  - `u64 onstack[12]`
- Helpers:
  - `bch2_bkey_buf_realloc_noprof()`
  - `bch2_bkey_buf_reassemble_noprof()`
  - `bch2_bkey_buf_copy_noprof()`
  - `bch2_bkey_buf_unpack_noprof()`
  - `bch2_bkey_buf_init()`
  - `bch2_bkey_buf_exit()`

## Behavior
- Starts with `k` pointing at `onstack`.
- If requested key size exceeds the inline array, allocates a fixed 2048-byte heap buffer with `GFP_KERNEL|__GFP_NOFAIL`.
- Reassemble/copy/unpack helpers ensure storage exists, then copy or unpack the key.
- Public macro wrappers route through `alloc_hooks()`.

## Risks / Review Notes
- Reallocation uses a fixed 2048-byte allocation, not `u64s * sizeof(u64)`. This assumes bkeys fit that allocation size in the relevant contexts.
- Allocation is no-fail once heap fallback is needed.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_cmp.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey_cmp.h

## Purpose
Defines hot inline packed-bkey comparison routines.

## Main Contents
- `__bkey_cmp_bits()`:
  - x86-64 inline assembly implementation for packed key bit comparison.
  - generic C fallback for non-x86-64.
- `__bch2_bkey_cmp_packed_format_checked_inlined()`: compares two packed keys using the btree’s packed format.
- `bch2_bkey_cmp_packed_inlined()`: handles packed-vs-packed hot path and mixed packed/unpacked cold path.

## Notable Details
- The x86-64 path walks high-order packed words and returns `-1/0/1`.
- Debug assertions compare packed comparison results against unpacked `bpos_cmp()` results.
- Mixed packed/unpacked comparison declares the temporary `struct bkey` only in the cold branch to avoid stack auto-init cost on the hot path.

## Risks / Review Notes
- The assembly is performance-driven and architecture-specific.
- Correctness depends on `high_word()`, endian definitions, and `b->nr_key_bits` matching `bkey_format_key_bits()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_cmp.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_methods.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey_methods.c

## Purpose
Implements bkey type operation dispatch: validation, text rendering, merging, compatibility conversion, byte swapping, key-type naming, and legacy key renumbering.

## Main Contents
- `bch2_bkey_types[]`: string table generated from `BCH_BKEY_TYPES()`.
- Per-type `bkey_ops` definitions for generic/core key types:
  - deleted
  - whiteout
  - extent_whiteout
  - error
  - cookie
  - hash_whiteout
  - inline_data
  - set
- `bch2_bkey_ops[]`: operation table generated from `BCH_BKEY_TYPES()`.
- `bch2_bkey_null_ops`: fallback for invalid/unknown types.

## Validation
- `bch2_bkey_val_validate()` checks minimum value size and dispatches per-type validation.
- `__bch2_bkey_validate()` checks:
  - `u64s >= BKEY_U64s`
  - key type allowed for the btree node type
  - extent keys have nonzero size and size <= offset
  - non-extent keys have size zero
  - snapshot field requirements by btree type
  - no non-btree key at `POS_MAX`
- `bch2_bkey_validate()` combines structural and value validation.
- Validation is bypassed when `BCH_FS_no_invalid_checks` is set.

## Text / Debug Rendering
- `bch2_bpos_to_text()` prints normal positions and sentinel values.
- `bch2_bkey_to_text()` prints key size, type, position, extent length, and version.
- `bch2_val_to_text()` and `bch2_bkey_val_to_text()` dispatch value rendering via `bkey_ops`.

## Merge And Trigger Support
- `bch2_bkey_merge()` checks type, version, adjacency, key size limits, global merge disable branch, and type-specific merge function.
- `KEY_TYPE_set` merges by extending the left key size.
- Header helpers use `bch2_key_trigger()` and `bkey_ops.trigger`.

## Compatibility
- `bch2_bkey_renumber()` maps older numeric key types to current type IDs depending on btree node type.
- `__bch2_bkey_compat()` applies read/write-compatible transformations in reversible order:
  - endian swap of key
  - legacy key renumbering
  - old inode btree inode/offset swap
  - pre-snapshot snapshot-field handling
  - value endian swap and type-specific compatibility callback

## Risks / Review Notes
- Compatibility transformations are order-sensitive and reversed on write.
- Validation strictness depends on context flags and btree type flags.
- Unknown key types route to null ops but may still be caught by strict allowed-type checks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_methods.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_methods.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey_methods.h

## Purpose
Declares the bkey operation interface and inline dispatch helpers for validation, text rendering, triggers, merges, repair, and compatibility.

## Main Types
- `struct bkey_ops` function table:
  - `key_validate`
  - `val_to_text`
  - `swab`
  - `key_merge`
  - `trigger`
  - `check_repair`
  - `compat`
  - `min_val_size`

## Main Helpers
- `bch2_bkey_type_ops(type)`: returns ops table entry or null ops.
- `bch2_bkey_maybe_mergable(l, r)`: checks type, version, and adjacency.
- `bch2_key_trigger()`: dispatches old/new trigger operation.
- `bch2_key_trigger_old()` and `bch2_key_trigger_new()` synthesize deleted old/new keys for overwrite/insert triggers.
- `bch2_bkey_check_repair()` dispatches optional repair hook.
- `bch2_bkey_compat()` conditionally calls full compatibility conversion only for old metadata, endian mismatch, or debug builds.

## External API
Declares validation, merge, text, swab, renumber, compatibility, and error-key helpers implemented in `bkey_methods.c`.

## Notable Details
- Trigger helpers construct local deleted keys at the same position to represent insertion/deletion transitions.
- Compatibility fast path avoids work when metadata is current and endian matches.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_methods.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey_types.h

## Purpose
Defines generic bkey wrapper types and generates typed wrappers/accessors for every bcachefs bkey value type.

## Main Concepts
The header includes embedded documentation explaining:
- `struct bpos` as search key: inode, offset, snapshot.
- `struct bkey` as key metadata plus value container header.
- Extent keys store end offset in `p.offset`; start is `p.offset - size`.
- Values are accessed through wrapper types because packed on-disk/in-node keys are often split into key and value pointers.

## Main Helpers
- `bkey_next()`
- `bkey_val_u64s()`
- `bkey_val_bytes()`
- `set_bkey_val_u64s()`
- `set_bkey_val_bytes()`
- `bkey_val_end()`
- deleted/whiteout predicates:
  - `bkey_deleted`
  - `bkey_whiteout`
  - `bkey_extent_whiteout`

## Wrapper Types
- `struct bkey_s_c`: const split key/value.
- `struct bkey_s`: mutable split key/value.
- null/error sentinel macros for both.
- Generic conversion helpers:
  - `bkey_to_s()`
  - `bkey_to_s_c()`
  - `bkey_i_to_s()`
  - `bkey_i_to_s_c()`

## Generated Typed Wrappers
The `BCH_BKEY_TYPES()` macro expansion generates, for each value type:
- `struct bkey_i_<name>`
- `struct bkey_s_<name>`
- `struct bkey_s_c_<name>`
- conversion helpers that assert `k->type == KEY_TYPE_<name>`
- initializer `bkey_<name>_init()` that zeroes value, sets type, and sets value size.

## Validation Context
- `enum bch_validate_flags`:
  - write
  - commit
  - silent
- `BKEY_VALIDATE_CONTEXTS()`:
  - unknown
  - superblock
  - journal
  - btree_root
  - btree_node
  - commit
- `struct bkey_validate_context` records source context, flags, btree id, level, root status, and journal location.

## Risks / Review Notes
- Typed conversions use `BUG_ON()` for type mismatch, so callers must switch/check type before converting.
- Value-size helpers assume `u64s >= BKEY_U64s`; structural validation elsewhere enforces that.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bkey_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bset.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bset.c

## Purpose
Implements bset operations inside a btree node: auxiliary search-tree construction, per-bset search, insertion/deletion maintenance, btree-node iteration across multiple bsets, diagnostics, and bset statistics.

## Core Model
A btree node contains multiple sorted bsets. Each bset stores variable-length packed bkeys, so direct binary search over the raw array is not practical. This file builds auxiliary lookup structures:
- read-write bsets use a simple offset table,
- read-only bsets use a compact Eytzinger-layout search tree of `struct bkey_float`.

## Diagnostics And Verification
- `bch2_btree_node_keys_to_text()`
- `bch2_bset_to_text()`
- `bch2_dump_btree_node_iter()`
- `bch2_btree_node_count_keys()`
- `__bch2_verify_btree_nr_keys()`
- iterator and insert-position verification under debug static branches

## Auxiliary Tree Structures
- `struct bkey_float`:
  - `exponent`
  - `key_offset`
  - `mantissa`
- `struct ro_aux_tree`: array of `bkey_float`.
- `struct rw_aux_tree`:
  - btree-node key offset
  - unpacked `bpos` for comparison
- `BKEY_MANTISSA_BITS` is 16.
- Failure sentinels mark bfloat entries that must fall back to full key comparison.

## Aux Tree Construction
- `bch2_btree_keys_init()` resets bset metadata and accounting.
- `bch2_bset_build_aux_tree()` allocates aux space and builds either writable or read-only structures.
- `__build_rw_aux_tree()` records periodic key offsets for the active write set.
- `__build_ro_aux_tree()` maps cachelines into Eytzinger nodes and builds bfloats.
- `make_bfloat()` chooses the mantissa/exponent based on key ranges and differing bits.

## Insert/Delete
- `bch2_bset_insert()`:
  - verifies insert position in debug mode,
  - attempts to pack the inserted key into the node format,
  - updates live-key accounting,
  - memmoves following keys if size changes,
  - copies packed key and value,
  - fixes writable lookup table.
- `bch2_bset_delete()`:
  - removes `clobber_u64s`,
  - shifts remaining keys down,
  - updates bset end and writable lookup table.

## Search
- `bset_search_write_set()` binary-searches the writable offset table.
- `bset_search_tree()` walks the read-only Eytzinger bfloat tree with prefetching and falls back to full comparison when bfloat precision is insufficient.
- `bch2_bset_search_linear()` finishes with a linear scan inside the selected cacheline/range.
- Search can use exact packed search, lossy packed search, or unpacked search depending on pack result.

## Node Iterator
- `bch2_btree_node_iter_init()` searches each bset, prefetches candidate cachelines, linearly finalizes each candidate, then sorts per-bset cursors.
- `bch2_btree_node_iter_init_from_start()` initializes iteration from all bset starts.
- `bch2_btree_node_iter_sort()` is an unrolled small bubble sort for up to `MAX_BSETS`.
- `bch2_btree_node_iter_advance()` advances the current lowest key and re-sorts.
- `bch2_btree_node_iter_prev_all()` is explicitly expensive and reconstructs previous position across bsets.
- `bch2_btree_node_iter_peek_unpack()` returns a disassembled key/value pair.

## Important Ordering Rule
Duplicate keys can exist when deleted keys are retained. The ordering puts deleted keys before live keys for equal positions, which is required by insertion and lookup semantics.

## Risks / Review Notes
- Aux-tree correctness relies on packed key comparison, lossy search keys, and bfloat fallback being conservative.
- `bch2_btree_node_iter_init()` has a special slow path when search-position packing fails; it starts from the beginning and advances linearly.
- Insert/delete maintenance only updates writable aux trees; read-only aux trees are rebuilt when needed.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bset.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bset.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bset.h

## Purpose
Declares bset and btree-node key-iteration APIs and documents the design of bsets, bkeys, btree node iterators, and auxiliary search trees.

## Main Concepts
- A bset is a contiguous sorted array of variable-length bkeys plus a header.
- A btree node consists of multiple bsets written at different times.
- In-memory nodes allow a bounded number of bsets and lazily rebuild/search them.
- Auxiliary structures index roughly one key per `BSET_CACHELINE` bytes, then finish by linear scan.

## Main Constants And Types
- `enum bset_aux_tree_type`:
  - `BSET_NO_AUX_TREE`
  - `BSET_RO_AUX_TREE`
  - `BSET_RW_AUX_TREE`
- `BSET_CACHELINE` is 256.
- Special `extra` values encode no-tree and writable-tree state.

## Helpers
- Aux tree classification:
  - `bset_aux_tree_type()`
  - `bset_has_ro_aux_tree()`
  - `bset_has_rw_aux_tree()`
  - `bch2_bset_set_no_aux_tree()`
- Btree node format setup:
  - `btree_node_set_format()` sets format, key bits, unpack constants, optional compiled format, and clears aux trees.
- Bset iteration macros:
  - `for_each_bset`
  - `for_each_bset_c`
  - `bset_tree_for_each_key`
- Key lookup support:
  - `bch2_bkey_to_bset_inlined()`
  - `bch2_bkey_prev_all()`
  - `bch2_bkey_prev()`
- Node iterator API:
  - init, push, sort, advance, prev, peek/unpack helpers.
- Accounting:
  - `btree_keys_account_key()`
  - `btree_keys_account_val_delta()`
  - add/drop macros
- Debug/statistics:
  - `struct bset_stats`
  - text dump declarations
  - debug verification wrappers

## Notable Details
- `btree_node_set_format()` also computes fast unpack constants and stores compiled-unpack length if enabled.
- Iterator comparison uses packed comparison and deleted-key tie-breaking.
- Iterator storage is small and fixed-size, matching the maximum number of in-memory bsets.

## Risks / Review Notes
- `BSET_CACHELINE` is a logical search granularity, not necessarily hardware cacheline size.
- Accounting helpers require the key to map to the correct bset; bad pointers will trip debug assertions or corrupt counts.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/bset.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/cache.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/cache.c

## Purpose
Implements the in-memory btree node cache: allocation, state transitions, hash lookup, pinning, reclaim/shrinker integration, cache cannibalization under memory pressure, btree-node fill/read paths, eviction, init/exit, evicted-size hints, and diagnostics.

## Cache Model
Btree nodes are hashed by physical on-disk pointer, not logical position, because bcachefs btree updates are copy-on-write. `struct btree` shells are normally retained until shutdown, allowing lock drop/reacquire patterns without refcounting.

## State Machine
`bch2_btree_node_transition_state_locked()` maintains the canonical cache states:
- `NONE`: off lists and not hashed.
- `FREED`: shell only, no data buffer.
- `FREEABLE`: unhashed with buffer, available for reuse.
- `CLEAN`: hashed/live, clean.
- `DIRTY`: hashed/live, dirty or write in flight.

The transition function handles:
- rhashtable insertion/removal,
- list movement,
- per-btree counts,
- pinned vs unpinned live lists,
- vmalloc accounting,
- buffer freeing,
- lock wakeups on identity removal.

## Allocation
- `__btree_node_data_alloc()` allocates node data and aux buffers with kernel/user differences:
  - kernel uses `kvmalloc`/`__vmalloc`,
  - userspace path can `mmap()` executable aux space.
- `__btree_node_mem_alloc()` creates the `struct btree` shell and initializes locks.
- `bch2_btree_node_mem_alloc()` first tries freeable nodes, self-reclaim under high memory pressure, allocator paths, freed shell reuse, and finally cannibalization.

## Pinning
- `__btree_node_pinned()` checks configured pinned ranges using `bbpos`.
- `bch2_node_pin()` moves a live node from unpinned to pinned lists.
- `bch2_btree_cache_unpin()` clears pin masks and splices pinned lists back into normal lists.

## Reclaim / Shrinker
- `bch2_btree_cache_scan()` reclaims from `freeable` and clean live lists while preserving reserve nodes.
- Reclaim skips permanent, noevict, write-blocked, will-make-reachable, dirty, read-in-flight, and write-in-flight nodes unless the caller allows dirty reclaim.
- Dirty cannibalized nodes are written before reuse.
- `not_freed[]` counters explain shrinker misses.

## Cannibalization
- `bch2_btree_cache_cannibalize_lock()` serializes emergency cache reuse through `bc->alloc_lock`.
- `btree_node_cannibalize()` searches clean lists first, then dirty lists with writeback/wait.
- This is used when normal node allocation fails and the transaction already holds the cannibalize lock.

## Lookup / Fill
- `btree_cache_find()` performs rhashtable lookup by btree pointer hash.
- `bch2_btree_node_fill()` allocates a node, validates pointer key shape, transitions it into the clean hash state, marks read-in-flight, unlocks for IO when needed, reads from disk, and relocks.
- `bch2_btree_node_get()` has a fast path through `btree_ptr_v2.mem_ptr`; it validates `hash_val`, locks the node, checks for reuse/read errors/read-in-flight, prefetches aux data, and verifies headers.
- `__bch2_btree_node_get()` is the slower lookup/fill/retry path.
- `bch2_btree_node_get_noiter()` provides lookup without a `btree_path`.
- `bch2_btree_node_prefetch()` starts async fill/read when absent.

## Eviction
`bch2_btree_node_evict()`:
- finds cached node,
- waits on read/write IO,
- locks intent/write,
- writes dirty nodes before eviction,
- records evicted live size,
- transitions to `FREED`.

Permanent/root nodes must not be evicted.

## Init / Exit
- `bch2_fs_btree_cache_init_early()` initializes locks and lists.
- `bch2_fs_btree_cache_init()` initializes rhashtable, reserve nodes, and two shrinkers: normal and pinned.
- `bch2_fs_btree_cache_exit()` frees shrinkers, drains write-complete workqueue, drains all live/freeable nodes to freed, frees shells, verifies counters, and destroys the hash table.

## Diagnostics
- `bch2_btree_id_str()`, `bch2_btree_id_to_text()`, and `bch2_btree_id_level_to_text()` print btree IDs.
- `bch2_btree_pos_to_text()` and `bch2_btree_node_to_text()` describe cached nodes.
- `bch2_btree_cache_to_text()` reports live/pinned/vmalloc/reserve/freeable/dirty/in-flight counts, per-btree memory, cannibalize state, and not-freed counters.
- `btree_cache_exit_locked_dump()` emits lock-owner diagnostics before teardown BUGs.

## Risks / Review Notes
- Correctness depends on checking identity after locking, because cache lookups race with node reuse.
- State transitions require write locks for hash/buffer transitions; assertions enforce this.
- Reclaim has to preserve reserve nodes to guarantee forward progress for btree updates.
- The userspace `mmap(PROT_EXEC)` aux-data allocation is tied to the dormant compiled-unpack path and may matter if that feature is re-enabled.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/cache.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/cache.h

## Purpose
Declares btree cache APIs and provides inline helpers for root packing, cache state inspection, node sizing, evicted-size hints, btree id lookup, and diagnostics.

## Main API Declarations
- cache lifecycle:
  - `bch2_fs_btree_cache_init_early()`
  - `bch2_fs_btree_cache_init()`
  - `bch2_fs_btree_cache_exit()`
- node allocation/free:
  - `__bch2_btree_node_mem_alloc()`
  - `bch2_btree_node_mem_alloc()`
  - `bch2_btree_node_mem_free()`
  - `bch2_btree_node_data_free()`
- cache state:
  - `bch2_btree_node_transition_state()`
  - `bch2_btree_node_transition_state_locked()`
  - `bch2_btree_node_set_dirty()`
  - `bch2_btree_node_write_done_clean()`
- lookup/fill/prefetch/evict:
  - `bch2_btree_node_get()`
  - `bch2_btree_node_get_noiter()`
  - `bch2_btree_node_prefetch()`
  - `bch2_btree_node_evict()`
- pinning and cannibalization:
  - `bch2_node_pin()`
  - `bch2_btree_cache_unpin()`
  - `bch2_btree_cache_cannibalize_lock()`
  - `bch2_btree_cache_cannibalize_unlock()`

## Inline Helpers
- Evicted-size table:
  - `btree_evicted_size_pack()`
  - `bch2_btree_evicted_size_record()`
  - `bch2_btree_evicted_size_lookup()`
- Btree pointer identity:
  - `btree_ptr_hash_val()`
  - `btree_node_mem_ptr()`
- Cache state:
  - `btree_node_hashed()`
  - `btree_node_cache_state()`
  - `btree_node_live_state()`
- Node sizing:
  - `btree_buf_bytes()`
  - `btree_buf_max_u64s()`
  - `btree_max_u64s()`
  - `btree_sectors()`
  - `btree_blocks()`
- Thresholds:
  - `BTREE_SPLIT_THRESHOLD`
  - foreground merge thresholds and hysteresis
- Root lookup and packing:
  - `bch2_btree_id_root()`
  - `bch2_btree_root_pack()`
  - `bch2_btree_root_unpack_b()`
  - `bch2_btree_root_unpack_level()`
  - `bch2_btree_id_root_packed()`
  - `bch2_btree_id_root_b()`
  - `btree_node_root()`
  - `btree_node_is_root()`

## Notable Details
- Root pointer and level are packed into one word using three low bits, relying on `struct btree` alignment.
- Standard roots use a hot side array `roots_b[]`; extra roots fall back to `roots_extra`.
- `btree_node_live_state()` treats dirty or write-in-flight nodes as `DIRTY`, otherwise `CLEAN`.
- `btree_node_buf_swap_account()` tracks vmalloc count when node buffers are swapped.

## Risks / Review Notes
- `btree_node_is_root()` assumes a root exists and compares levels; callers must use it only when root lookup is valid.
- Packed root pointer helpers depend on pointer alignment and `BTREE_MAX_DEPTH` fitting in three bits.
- `btree_ptr_hash_val()` reads raw little-endian-ish fields through casts to avoid sparse warnings; it is identity-oriented, not semantic decoding.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/cache.h -->