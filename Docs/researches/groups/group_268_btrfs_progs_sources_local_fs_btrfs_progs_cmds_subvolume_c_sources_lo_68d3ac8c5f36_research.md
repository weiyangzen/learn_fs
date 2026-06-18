# Group Research: group_268_btrfs_progs_sources_local_fs_btrfs_progs_cmds_subvolume_c_sources_lo_68d3ac8c5f36

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/btrfs-progs`, which is in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/subvolume.c -->
# File Research: sources/local-fs/btrfs-progs/cmds/subvolume.c

## Purpose
Implements the `btrfs subvolume` command group for btrfs-progs: create, delete, list integration, snapshot, get/set-default, find-new, show, and sync. It is CLI glue around `libbtrfsutil`, btrfs ioctls, qgroup helpers, formatting helpers, and common path/open/device utilities.

## Key Interfaces And Flow
- Defines `btrfs_subvolume_rowspec[]`, shared JSON/text output schema for subvolume fields, UUIDs, times, qgroup stats, and snapshot lists.
- `cmd_subvolume_create()` parses `-i` qgroup inheritance and `-p/--parents`, then calls `create_one_subvolume()` for each destination.
- `cmd_subvolume_delete()` supports path deletion, `--subvolid`, commit modes, recursive deletion printing, dry-run, default-subvolume protection, and final per-filesystem sync for `--commit-after`.
- `cmd_subvolume_snapshot()` validates source/destination, derives destination name when a directory is given, and creates read-write or read-only snapshots with optional qgroup inheritance.
- `cmd_subvolume_get_default()` and `cmd_subvolume_set_default()` query or set the default root by path or explicit root id.
- `cmd_subvolume_find_new()` uses tree-search ioctls to print file extents changed since a generation marker.
- `cmd_subvolume_show()` resolves a subvolume by path, root id, or UUID, prints metadata, child snapshots, and qgroup usage.
- `cmd_subvolume_sync()` waits for deleted subvolume ids to disappear, either explicitly supplied or discovered via `btrfs_util_subvolume_list_deleted_fd()`.
- Registers the command group through `subvolume_cmd_group` and `DEFINE_GROUP_COMMAND_TOKEN(subvolume)`.

## Dependencies
Uses `libbtrfsutil` for high-level subvolume operations, `BTRFS_IOC_INO_LOOKUP` and tree-search ioctls for low-level generation/path discovery, qgroup code from `cmds/qgroup.h`, formatter rowspecs from `common/format-output.h`, and many common path/open/message helpers.

## Notable Behaviors
- Delete protects the current default subvolume by comparing target id to `btrfs_util_subvolume_get_default_fd()`.
- Recursive delete is delegated to `BTRFS_UTIL_DELETE_SUBVOLUME_RECURSIVE`, but it first attempts a post-order iterator pass to print nested subvolumes.
- `--commit-after` keeps one fd per seen fsid so a final sync is issued once per filesystem.
- `find-new` syncs the filesystem before searching, then uses cached inode/path resolution to reduce repeated tree lookups.
- JSON output is conditionally enabled for some commands under `EXPERIMENTAL`.

## Risks And Review Notes
- `qgroup_inherit_add_group(struct ..., const char *arg)` ignores `arg` and reads global `optarg`; current callers pass `optarg`, but the function signature is misleading and fragile.
- `print_subvolume_show_text()` prints `Send time` before formatting `subvol->stime`, so send time appears to reuse the previous creation-time string or `-`.
- `uuid_parse()` return value in `cmd_subvolume_show()` is not checked, so invalid UUID text may become an unintended lookup key.
- `create_one_subvolume()` builds parent directories with fixed `PATH_MAX` buffers and repeated `strcat()`; very long paths depend on prior truncation behavior from `strncpy_null()`.
- `wait_for_subvolume_cleaning()` returns `-errno` after `error_btrfs_util(err)`, but `errno` reliability depends on libbtrfsutil setting it for every error.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/subvolume.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/subvolume.h -->
# File Research: sources/local-fs/btrfs-progs/cmds/subvolume.h

## Purpose
Small public header for subvolume command formatting metadata.

## Contents
- Include guard `__BTRFS_SUBVOLUME_H__`.
- Forward declares `struct rowspec`.
- Exports `extern const struct rowspec btrfs_subvolume_rowspec[];`.

## Integration
Allows other command code to reuse the subvolume rowspec array without including the large `subvolume.c` implementation.

## Risks
No logic. Compatibility risk is limited to keeping the declaration synchronized with the definition in `cmds/subvolume.c`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/cmds/subvolume.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/bitmap.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/bitmap.h

## Purpose
Userspace wrapper for a small subset of Linux bitmap helpers used by btrfs-progs.

## Key Interfaces
- `bitmap_zalloc(nbits)` allocates zeroed storage sized by `BITS_TO_LONGS(nbits)`.
- `bitmap_free(bitmap)` frees bitmap storage.
- `bitmap_weight(bitmap, nbits)` returns the number of set bits in a bitmap.

## Dependencies
Includes `kerncompat.h`, `<stdlib.h>`, and `kernel-lib/bitops.h`.

## Risks And Review Notes
- `bitmap_zalloc()` calls `calloc(BITS_TO_LONGS(nbits), BITS_PER_LONG)`. Since `BITS_PER_LONG` is a bit count, not bytes, this overallocates by a factor of 8 on typical platforms. It is wasteful but usually safe.
- `bitmap_weight()` handles the trailing partial word as `ret += bitmap[i] & BITMAP_LAST_WORD_MASK(nbits)` rather than applying `hweight_long()` to the masked value. That overcounts whenever the masked low bits form a numeric value greater than their popcount.
- Macro typo `BITMAP_LAST_WORK_MASK` is defined but unused; the function uses `BITMAP_LAST_WORD_MASK` from `bitops.h`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/bitops.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/bitops.h

## Purpose
Userspace bit operation helpers modeled after Linux/perf code.

## Key Interfaces
- Bitmap sizing and indexing macros: `BITS_TO_LONGS`, `BITS_TO_U64`, `BIT_MASK`, `BIT_WORD`.
- Iteration macros: `for_each_set_bit`, `for_each_set_bit_from`.
- Bit mutation/test helpers: `set_bit`, `clear_bit`, `test_and_set_bit`.
- Hamming weight helpers: `hweight32`, `hweight64`, `hweight_long`.
- Search helpers: `__ffs`, `ffz`, `_find_next_bit`, `find_next_bit`, `find_next_zero_bit`, first-bit aliases.
- Little-endian bit scanning helpers, with byte-swapped implementations for big-endian hosts.

## Dependencies
Includes `kerncompat.h`, `<endian.h>`, and `common/internal.h` for common types/macros such as `round_down`, `min`, and endian utilities.

## Notable Behaviors
- Bit searches return `size`/`nbits` when no matching bit exists.
- `_find_next_bit()` optionally intersects `addr1` and `addr2`, though this file only exposes public wrappers for the single-address cases.
- Big-endian `_le` functions use `ext2_swab()` to emulate little-endian bitmap numbering.

## Risks
- Helpers are non-atomic despite kernel-like names; suitable for userspace single-threaded or externally synchronized use.
- `__ffs()` is undefined for zero input by contract; callers must guard.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/interval_tree_generic.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/interval_tree_generic.h

## Purpose
Macro template for generating augmented red-black interval-tree implementations.

## Key Interface
- `INTERVAL_TREE_DEFINE(...)` emits prefixed insert/remove/search/iteration functions for a caller-provided node type and interval endpoint accessors.

## Generated Behavior
- Maintains an augmented `ITSUBTREE` field containing the maximum interval end in each subtree.
- Inserts nodes ordered by interval start.
- Removes nodes through `rb_erase_augmented()`.
- Supports `iter_first(root, start, last)` and `iter_next(node, start, last)` over intervals intersecting `[start, last]`.

## Dependencies
Uses `kernel-lib/rbtree_augmented.h`.

## Risks
- This is a macro code generator; correctness depends on caller-supplied `ITSTART`, `ITLAST`, field names, and update discipline.
- It assumes closed intervals and requires the caller’s endpoint type comparisons to be valid for all represented ranges.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/interval_tree_generic.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/list.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/list.h

## Purpose
Userspace copy/adaptation of Linux intrusive doubly-linked list and hlist primitives.

## Key Interfaces
- `struct list_head`, `struct hlist_head`, `struct hlist_node`.
- Initialization macros/functions: `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, `HLIST_HEAD`, `INIT_HLIST_HEAD`, `INIT_HLIST_NODE`.
- List mutation: `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_replace`, `list_swap`, `list_move`, `list_bulk_move_tail`, splice/cut helpers.
- List queries: `list_empty`, `list_empty_careful`, `list_is_first`, `list_is_last`, `list_is_singular`.
- Typed entry and iteration macros, including safe variants for deletion during iteration.
- Hlist mutation/query/iteration helpers.

## Dependencies
Includes `kerncompat.h`, `<stddef.h>`, and `<stdbool.h>`. Uses `container_of`, `READ_ONCE`, `WRITE_ONCE`, and optional debug validation hooks.

## Notable Behaviors
- Poison pointers are assigned after destructive deletion to catch misuse.
- `list_empty_careful()` uses acquire/release-style wrappers for the limited synchronization pattern documented in the file.
- Hlist nodes track predecessor link by pointer-to-pointer, enabling O(1) deletion without a full doubly linked head.

## Risks
- These primitives do not own storage or enforce lifetime; use-after-free and double deletion remain caller responsibilities.
- Debug validation is compiled out unless `CONFIG_DEBUG_LIST` is provided.
- Concurrency safety is minimal and mirrors the comments: most use requires external locking.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/list.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/list_sort.c -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/list_sort.c

## Purpose
Stable merge sort for `struct list_head` lists, adapted from Linux `lib/list_sort.c`.

## Key Interface
- `list_sort(void *priv, struct list_head *head, int (*cmp)(...))`.

## Implementation
- Converts the circular doubly linked list into null-terminated forward lists.
- Accumulates sorted partial lists in `part[MAX_LIST_LENGTH_BITS + 1]`.
- Uses stable merge behavior: equal elements choose the left input first.
- Final merge restores `prev` links and the circular sentinel head.

## Dependencies
Includes `kerncompat.h`, `stdio.h`, `string.h`, `kernel-lib/list_sort.h`, and `kernel-lib/list.h`.

## Risks
- Lists longer than the fixed partial-list capacity trigger a warning and reduce efficiency, but still continue.
- During final back-link restoration, `cmp(priv, tail->next, tail->next)` is called intentionally; comparators must tolerate identical arguments.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/list_sort.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/list_sort.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/list_sort.h

## Purpose
Declaration header for the list sort helper.

## Contents
- Include guard `_LINUX_LIST_SORT_H`.
- Forward declares `struct list_head`.
- Declares `list_sort()`.

## Risks
No logic. The comparator contract is documented in `list_sort.c`, not this header.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/list_sort.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/mktables.c -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/mktables.c

## Purpose
Build-time generator for RAID-6 Galois-field lookup tables.

## Key Flow
- `gfmul(a, b)` performs GF(2^8) multiplication with polynomial reduction `0x1d`.
- `gfpow(a, b)` computes powers modulo the 255-element nonzero field cycle.
- `main()` prints C definitions for:
  - `raid6_gfmul[256][256]`
  - `raid6_vgfmul[256][32]`
  - `raid6_gfexp[256]`
  - `raid6_gfinv[256]`
  - `raid6_gfexi[256]`

## Integration
Generated output is consumed by RAID6 recovery/generation code declared in `raid56.h` and used in `raid56.c`.

## Risks
- Generator output is deterministic but large; build integration must ensure generated tables match the declarations’ alignment/type expectations.
- No argument handling is needed; any command-line arguments are ignored.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/mktables.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/overflow.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/overflow.h

## Purpose
Linux-style integer overflow and allocation-size helper macros for userspace builds.

## Key Interfaces
- Type property macros: `is_signed_type`, `type_min`, `type_max`, `is_negative`, `is_non_negative`.
- `__must_check` support through `__must_check_overflow()`.
- Arithmetic checks: `check_add_overflow`, `check_sub_overflow`, `check_mul_overflow`, `check_shl_overflow`.
- Saturating size helpers: `size_mul`, `size_add`, `size_sub`, `array_size`, `array3_size`, `flex_array_size`, `struct_size`.

## Dependencies
Includes `<stdbool.h>`, `<stddef.h>`, and `<stdint.h>`. Relies on configure-provided `HAVE___BUILTIN_*_OVERFLOW` macros and compiler extensions like `typeof`, statement expressions, and `__builtin_choose_expr`.

## Risks And Review Notes
- Fallback definitions for missing compiler builtins do not actually detect overflow; they assign the wrapped result and return false.
- The fallback guard for `__builtin_sub_overflow` checks `!HAVE___BUILTIN_MUL_OVERFLOW`, which looks like a copy/paste error; it should likely be controlled by a subtraction-specific configure macro.
- Type-checking intentionally requires operands and destination pointed-to type to match, which is stricter than GCC builtins.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/overflow.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/raid56.c -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/raid56.c

## Purpose
Portable userspace RAID5/RAID6 parity generation and recovery helpers for btrfs-progs.

## Key Interfaces
- `raid6_gen_syndrome(disks, bytes, ptrs)` generates P and Q syndrome blocks.
- `raid5_gen_result(nr_devs, stripe_len, dest, data)` regenerates a RAID5 missing stripe by XOR.
- `raid6_recov_data2(...)` recovers two missing RAID6 data stripes.
- `raid6_recov_datap(...)` recovers one data stripe plus P parity.
- `raid56_recov(...)` dispatches RAID5/RAID6 recovery based on btrfs profile and missing stripe indexes.

## Dependencies
Includes volume/profile definitions, btrfs tree constants, RAID table declarations from `raid56.h`, and message helpers.

## Notable Behaviors
- Uses native-word unaligned loads/stores for portable syndrome generation.
- RAID5 with two devices is treated as RAID1 and copied from the mirror.
- `raid56_recov()` normalizes `dest1`/`dest2`, rejects unrecoverable RAID5 dual failures, regenerates P/Q directly when only parity is missing, and handles data+Q by data recovery followed by full syndrome regeneration.

## Risks And Review Notes
- `raid6_recov_datap()` allocates `zero_mem` but does not free it before returning, causing a leak per call.
- `raid6_recov_datap()` lacks the argument validation present in `raid6_recov_data2()`; wrapper paths constrain callers, but direct callers could pass invalid indexes.
- `raid5_gen_result()` requires `stripe_len == BTRFS_STRIPE_LEN`; this rejects other lengths even though the parameter type is general.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/raid56.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/raid56.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/raid56.h

## Purpose
Public declarations for RAID5/6 generation and recovery helpers plus generated RAID6 lookup tables.

## Contents
- Declares `raid6_gen_syndrome()` and `raid5_gen_result()`.
- Exports aligned GF lookup tables generated by `mktables.c`.
- Declares RAID6 recovery helpers and top-level `raid56_recov()`.

## Integration
Included by `raid56.c` and any code needing parity reconstruction for btrfs RAID56 profiles.

## Risks
Header comments define return semantics for `raid56_recov()`: positive means unrecoverable, zero recovered/no-op, negative fatal error. Callers must not collapse all nonzero values without preserving this distinction when diagnostics matter.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/raid56.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/rbtree.c -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/rbtree.c

## Purpose
Userspace adaptation of Linux red-black tree insertion, deletion, replacement, and iteration.

## Key Interfaces Implemented
- Rebalancing: `rb_insert_color`, `rb_erase`, `__rb_insert_augmented`, `__rb_erase_color`.
- Ordered traversal: `rb_first`, `rb_last`, `rb_next`, `rb_prev`.
- Replacement: `rb_replace_node`.
- Postorder traversal: `rb_first_postorder`, `rb_next_postorder`.

## Dependencies
Includes `kerncompat.h`, rbtree type/header files, and augmented rbtree declarations.

## Notable Behaviors
- Parent pointer and color are packed in `__rb_parent_color`.
- Rotations use `WRITE_ONCE()` for child pointers to support lockless lookup constraints described in comments.
- Non-augmented operations use dummy augment callbacks so common augmented erase/insert code can be reused.
- Deletion handles standard red-black erase cases and returns a rebalance parent for augmented callers.

## Risks
- The API provides tree mechanics only; caller code must implement ordering and search correctly.
- Lockless traversal comments guarantee termination and valid elements, not a consistent snapshot.
- Misuse of `rb_replace_node()` with an already-linked replacement node would corrupt tree structure.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/rbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/rbtree.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/rbtree.h

## Purpose
Public rbtree API and inline helper layer.

## Key Interfaces
- Basic macros: `rb_parent`, `rb_entry`, `RB_EMPTY_ROOT`, `RB_EMPTY_NODE`, `RB_CLEAR_NODE`.
- Core declarations for insert/erase/traversal/replacement.
- `rb_link_node()` for caller-managed insertion.
- Cached-leftmost helpers: `rb_first_cached`, `rb_insert_color_cached`, `rb_erase_cached`, `rb_replace_node_cached`.
- Generic inline helpers: `rb_add`, `rb_add_cached`, `rb_find_add`, `rb_find`, `rb_find_first`, `rb_next_match`, `rb_for_each`.
- Postorder safe iteration macro.

## Dependencies
Includes `kerncompat.h` and `rbtree_types.h`, with flat and installed include path variants.

## Notable Behaviors
- The API deliberately avoids generic callbacks for core search/insert in performance-sensitive paths; callers usually write their own comparison logic.
- `rb_find_first()` plus `rb_next_match()` supports duplicate-equivalent keys when the comparator groups multiple nodes.

## Risks
- Comparator consistency is critical; partial orders may return any equivalent node except where first-match helpers are used.
- `rbtree_postorder_for_each_entry_safe()` allows freeing the current entry but cannot tolerate tree rebalancing during iteration.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/rbtree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/rbtree_augmented.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/rbtree_augmented.h

## Purpose
Augmented red-black tree support: callbacks and erase/insert helpers that maintain caller-defined subtree metadata.

## Key Interfaces
- `struct rb_augment_callbacks` with `propagate`, `copy`, and `rotate`.
- `rb_insert_augmented()`, `rb_insert_augmented_cached()`.
- `RB_DECLARE_CALLBACKS(...)` macro to generate standard augmentation callbacks.
- Internal color/parent helpers and `__rb_erase_augmented()`.
- `rb_erase_augmented()`, `rb_erase_augmented_cached()`.

## Dependencies
Includes `kernel-lib/rbtree.h`.

## Notable Behaviors
- Insert expects caller to update augmented data on the path before calling the augmented insert helper.
- Erase copies augmentation data to successor nodes and propagates updates upward.
- Cached erase updates `rb_leftmost` before rebalancing.

## Risks
- Public comments warn that most definitions are implementation details; external users should depend only on callback structs and augmented insert/erase APIs.
- Incorrect `propagate/copy/rotate` callbacks silently break data structures such as interval trees.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/rbtree_augmented.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/rbtree_types.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/rbtree_types.h

## Purpose
Minimal rbtree type definitions shared by rbtree headers and users.

## Contents
- `struct rb_node` with packed parent/color and left/right child pointers, aligned to `sizeof(long)`.
- `struct rb_root`.
- `struct rb_root_cached` with cached leftmost node.
- Initializers `RB_ROOT` and `RB_ROOT_CACHED`.
- C++ extern guard.

## Risks
No logic. ABI compatibility depends on keeping this layout aligned with rbtree implementation expectations.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/rbtree_types.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/sizes.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/sizes.h

## Purpose
Linux-style size constants for powers of two from bytes through GiB.

## Contents
Defines `SZ_1` through `SZ_512`, `SZ_1K` through `SZ_512K`, `SZ_1M` through `SZ_512M`, and `SZ_1G`/`SZ_2G`.

## Integration
Used by mkfs sizing code, especially `mkfs/common.h` and `mkfs/common.c`.

## Risks
Constants are untyped integer macros. Large values such as `SZ_2G` may need explicit casting in signed 32-bit contexts.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/sizes.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/trace.h -->
# File Research: sources/local-fs/btrfs-progs/kernel-lib/trace.h

## Purpose
No-op tracepoint stubs for userspace builds that share code with kernel-origin btrfs components.

## Contents
Forward declares several btrfs structures and defines empty inline functions for workqueue, ordered work, extent state, extent bit, and COW block tracepoints.

## Integration
Lets shared code compile without carrying Linux kernel tracing infrastructure.

## Risks
- All trace calls are compiled away; diagnostics relying on kernel tracepoints are unavailable in btrfs-progs.
- Function signatures must stay synchronized with shared code call sites.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/kernel-lib/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/Makefile -->
# File Research: sources/local-fs/btrfs-progs/mkfs/Makefile

## Purpose
Small recursive make wrapper for mkfs-related build targets.

## Contents
- Includes `../Makefile.inc`.
- `all` invokes `$(MAKE) -C .. mkfs.btrfs`.
- `clean` removes local `*.o` and `*.o.d`.

## Risks
No complex logic. The directory relies on the parent makefile for actual build rules.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/common.c -->
# File Research: sources/local-fs/btrfs-progs/mkfs/common.c

## Purpose
Common mkfs implementation for creating the initial btrfs filesystem image and validating target devices/files before formatting.

## Key Creation Flow
- `make_btrfs(fd, cfg)` assembles a temporary-signature filesystem with initial system chunk, root tree, extent tree, chunk tree, device tree, fs tree, checksum tree, optional free-space tree, and optional block-group tree.
- Initializes UUIDs, superblock fields, feature flags, csum type, label, device item, sys chunk array, and initial tree blocks.
- Writes all initial tree blocks with checksums, then writes the superblock using `BTRFS_MAGIC_TEMPORARY` and `sbwrite()`, followed by `fsync()`.

## Important Helpers
- `btrfs_write_empty_tree()` writes an empty leaf/tree root for a given objectid.
- `btrfs_create_tree_root()` creates root items for initial trees and initializes the FS tree root UUID/timestamps.
- `create_free_space_tree()` writes free-space info and one free extent for the initial system group.
- `write_block_group_item()` and `create_block_group_tree()` serialize block group items, including v2/remap-tree fields.
- `zoned_system_group_offset()` chooses a system group zone that avoids superblock zones.
- `mkfs_blocks_add()` and `mkfs_blocks_remove()` maintain the initial tree-block list.
- `btrfs_min_dev_size()` estimates minimum device size for zoned, mixed, single, and profiled data/metadata layouts.
- `test_dev_for_mkfs()`, `test_status_for_mkfs()`, `test_minimum_size()`, `is_swap_device()`, and `check_overwrite()` protect against formatting swap, mounted, too-small, or already-formatted devices.

## Dependencies
Uses btrfs shared accessors/disk-io/volume/zoned code, common feature definitions, open/device/string/message helpers, libblkid probing, and UUID generation.

## Notable Behaviors
- Initial filesystem uses one system chunk mapped 1:1 at the reserved/system offset.
- Free-space-tree and block-group-tree initialization is feature-flag controlled.
- Zoned mode uses zone-sized system groups and sets cache generation differently.
- Existing signatures are detected with blkid and a manual zoned btrfs signature fallback at offset 0.
- `/proc/swaps` entries are decoded for octal escapes before stat comparisons.

## Risks And Review Notes
- `mkfs_blocks_add()` uses `memmove(blocks + i + 1, blocks + i, *blocks_nr - i)` with a byte count that is missing `sizeof(*blocks)`. Because enum size is usually 4 bytes, this moves too few bytes when inserting before existing entries. Current call patterns may avoid harmful insertion positions, but the helper itself is wrong.
- `check_overwrite()` treats blkid probe errors and “nothing found” as reasons to run the zoned-signature fallback; this is conservative, but can produce warnings from devices that are unreadable at offset 0.
- `force_overwrite` skips signature checks but not mount checks unless mount status cannot be determined, where it warns and proceeds.
- `make_btrfs()` writes a temporary magic superblock; callers must finalize the filesystem after this initial image phase.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/common.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/common.h -->
# File Research: sources/local-fs/btrfs-progs/mkfs/common.h

## Purpose
Public mkfs common API and configuration definitions.

## Key Contents
- Defines initial mkfs constants: `BTRFS_MKFS_SYSTEM_GROUP_SIZE`, `BTRFS_MKFS_SMALL_VOLUME_SIZE`, and default one-device/multi-device data/metadata profiles.
- Defines `enum btrfs_mkfs_block` for initial tree blocks and `MKFS_BLOCK_COUNT`.
- Defines `default_blocks[]` with the default initial tree block set.
- Defines `struct btrfs_mkfs_config`, including input settings, feature flags, sizes, checksumming, zone size, output block addresses, UUID strings, and superblock offset.
- Declares `make_btrfs()`, minimum-size/profile validation helpers, and target-device status checks.

## Dependencies
Includes `kerncompat.h`, `<stdbool.h>`, `kernel-lib/sizes.h`, btrfs UAPI constants, common definitions, and fs feature types.

## Risks
- `default_blocks[]` is a `static const` array in a header, so each translation unit gets its own copy. That is acceptable for a small constant table but should remain intentional.
- `cfg->blocks` is sized as `MKFS_BLOCK_COUNT + 1`, while enum values are currently below `MKFS_BLOCK_COUNT`; the extra slot is unused defensive space.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/common.h -->