# Group Research: group_202_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_Kconfig_sources_cow__5b0a86f086f0

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/Kconfig -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/Kconfig

This file defines the kernel configuration surface for the bcachefs filesystem.

`BCACHEFS_FS` is the main tristate option, marked experimental, depending on `BLOCK` and selecting the filesystem, crypto, compression, RAID/parity, checksum, key, and support libraries bcachefs needs. The help text describes bcachefs as a modern copy-on-write filesystem with multiple-device, compression, and checksumming support.

Additional options expose feature and debug knobs:
- `BCACHEFS_QUOTA` depends on `BCACHEFS_FS` and selects `QUOTACTL`.
- `BCACHEFS_DEBUG` enables extra assertions and checks, with expected performance cost.
- `BCACHEFS_INJECT_TRANSACTION_RESTARTS` depends on debug and randomly injects transaction restarts in core paths.
- `BCACHEFS_TESTS` includes unit/performance tests for core btree code.
- `BCACHEFS_LOCK_TIME_STATS` exposes lock hold-time stats in debugfs.
- `BCACHEFS_NO_LATENCY_ACCT` disables device latency tracking and timing stats for performance testing.
- `BCACHEFS_SIX_OPTIMISTIC_SPIN` defaults on for SMP and enables optimistic spinning on six locks.
- `BCACHEFS_PATH_TRACEPOINTS` adds high-volume btree path tracepoints when tracing is available.
- `BCACHEFS_TRANS_KMALLOC_TRACE` traces transaction allocation calls.
- `MEAN_AND_VARIANCE_UNIT_TEST` wires the bcachefs utility KUnit test into `KUNIT_ALL_TESTS`.

There is also a `BCACHEFS_DKMS` conditional that forces `CONFIG_BCACHEFS_FS := m` for DKMS builds. This file is purely build/configuration policy; it does not implement runtime logic, but it controls whether the allocation/accounting code in this group is compiled and what debug instrumentation may be active.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/Makefile -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/Makefile

This is the kbuild file for the bcachefs module/object.

When `CONFIG_BCACHEFS_FS` is enabled, `bcachefs.o` is built. `bcachefs-y` enumerates the module’s object files. The files in this research group are part of the allocation subsystem entries near the top:
- `alloc/accounting.o`
- `alloc/background.o`
- `alloc/backpointers.o`
- `alloc/buckets.o`
- `alloc/check.o`

The Makefile then lists the broader implementation: allocation helpers, btree code, data/checksum/compression/copygc/erasure coding, filesystem operations, initialization/recovery, journal code, superblock handling, snapshots, utilities, vendor support, and VFS integration.

Conditional additions:
- `debug/async_objs.o` is included when `CONFIG_DEBUG_FS` is enabled.
- `util/mean_and_variance_test.o` is included for `CONFIG_MEAN_AND_VARIANCE_UNIT_TEST`, except in DKMS builds.
- `module-version.o` is added for DKMS builds.

It also disables noisy `psabi` compiler warnings and explicitly adds `-I$(src)` because kbuild sometimes does not pass the source include path consistently. The Makefile establishes that the allocation/accounting files are core bcachefs objects, not optional side modules.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting.c

This file implements bcachefs disk accounting: persistent accounting keys in the accounting btree plus fast in-memory per-CPU counters.

Core model:
- Persistent accounting uses `KEY_TYPE_accounting` entries in `BTREE_ID_accounting`.
- Updates are deltas queued through the btree write buffer.
- In-memory accounting stores selected accounting keys in an Eytzinger-sorted dynamic array of `accounting_mem_entry`, each with per-CPU counter arrays.
- Commit assigns each accounting delta a journal-position-derived `bversion`, allowing journal replay to distinguish already-applied updates from unapplied deltas.

Important functions:
- `bch2_disk_accounting_mod()` normalizes accounting keys, coalesces duplicate deltas in the transaction accounting buffer, removes zeroed deltas, or applies GC-mode updates directly to memory accounting.
- `bch2_mod_dev_cached_sectors()` is a helper for cached replicas accounting.
- `bch2_accounting_validate()` validates accounting key structure, replicas fields, zero padding, counter count, and nonzero versions at commit validation time.
- `bch2_accounting_key_to_text()` and `bch2_accounting_to_text()` render accounting keys and counters.
- `bch2_accounting_swab()` byte-swaps accounting values.
- `bch2_accounting_update_sb()` ensures replicas accounting keys being updated are represented in the superblock replicas table when needed.

Memory accounting:
- `__bch2_accounting_mem_insert()` inserts a new accounting memory entry, allocates per-CPU counters, and sorts the Eytzinger array.
- `bch2_accounting_mem_insert()` may temporarily drop the per-CPU read lock to take the write lock and insert.
- `bch2_accounting_mem_insert_locked()` assumes the caller already holds the relevant write lock.
- `__bch2_accounting_maybe_kill()` removes zero-valued replicas accounting entries and updates the superblock.
- `bch2_accounting_mem_gc()` removes zero in-memory entries.

Read APIs:
- `bch2_fs_replicas_usage_read()` emits replicas usage records for the existing userspace usage ioctl.
- `bch2_fs_accounting_read()` exports selected in-memory accounting keys as serialized accounting bkeys.
- `bch2_fs_accounting_read_key()` reads either from memory accounting or directly from the accounting btree for non-memory accounting types.

GC accounting:
- `bch2_gc_accounting_start()` allocates a second per-CPU counter set for GC-computed values.
- `bch2_gc_accounting_done()` compares normal counters with GC counters, reports mismatches, and can repair persistent accounting by writing corrective deltas.
- `bch2_accounting_gc_free()` frees GC counter arrays and clears `gc_running`.

Mount/replay initialization:
- `bch2_accounting_read()` rebuilds in-memory accounting from the accounting btree and journal keys. It walks btree and journal accounting together, discards old journal deltas based on `bversion`, accumulates newer deltas by key, compacts journal keys, sorts memory entries, asserts no duplicates, then runs fixups.
- `accounting_read_mem_fixups()` drops zero/invalid entries, validates late references to devices and replicas-superblock entries, populates aggregate filesystem and per-device counters, and schedules `check_allocations` if underflow is detected.

Repair and device removal:
- `disk_accounting_invalid_dev()` removes accounting entries pointing to invalid devices by adding a negated delta and committing it.
- `bch2_disk_accounting_validate_late()` handles validity checks that need live filesystem state.
- `bch2_dev_usage_remove()` removes all `dev_data_type` accounting for a device.
- `bch2_dev_usage_init()` initializes free bucket accounting for a device.
- `bch2_verify_accounting_clean()` debug-checks persistent accounting against in-memory counters and aggregate capacity usage.
- `bch2_fs_accounting_exit()` frees all memory accounting storage.

Key invariants:
- Accounting updates are deltas until write-buffer flush or journal replay resolves them.
- Accounting key versions must be strictly time ordered.
- Memory accounting is only maintained for selected types: not `snapshot` or `inum`.
- Replicas accounting may require superblock updates before insertion.
- Normal accounting updates also maintain aggregate `fs_usage_delta` and per-device usage counters.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting.h

This header exposes disk accounting helpers, transaction hooks, and in-memory accounting operations.

Counter helpers:
- `bch2_u64s_neg()` negates a vector of counters.
- `bch2_accounting_counters()` derives the number of counters from a `KEY_TYPE_accounting` value size.
- `bch2_accounting_neg()`, `bch2_accounting_key_is_zero()`, and `bch2_accounting_accumulate()` manipulate accounting values.
- `bch2_accounting_accumulate_maybe_kill()` accumulates and removes zeroed replicas entries when appropriate.

Filesystem usage helpers:
- `fs_usage_data_type_to_base()` maps `BCH_DATA_btree`, user/parity, and cached data types into aggregate filesystem usage fields.

Position conversion:
- `bpos_to_disk_accounting_pos()` and `disk_accounting_pos_to_bpos()` reinterpret accounting keys as btree positions, with byte swapping on little-endian systems so the typed union sorts correctly as a `bpos`.

API and convenience macros:
- `bch2_disk_accounting_mod()` is the main update API.
- `disk_accounting_key_init()` initializes typed accounting keys.
- `bch2_disk_accounting_mod2()` builds a typed key inline and submits a delta.
- `bch2_fs_accounting_read_key2()` is the analogous typed-key read helper.

Bkey operations:
- `bch2_bkey_ops_accounting` supplies validation, text rendering, byte swap, and minimum value size for accounting bkeys.

In-memory accounting:
- `enum bch_accounting_mode` distinguishes normal, GC, and read initialization paths.
- `bch2_accounting_is_mem()` identifies accounting types mirrored in memory.
- `bch2_bkey_is_accounting_mem()` checks whether a bkey is an in-memory accounting key.
- `bch2_accounting_mem_mod_locked()` is the hot path called from transaction commit. It updates aggregate filesystem usage, per-device usage, and the matching per-CPU accounting entry. It inserts missing memory entries when needed.

Transaction hooks:
- `journal_pos_to_bversion()` converts a journal reservation and offset into a unique accounting version.
- `bch2_accounting_trans_commit_hook()` stamps accounting deltas with versions and applies them to memory counters unless accounting apply is skipped.
- `bch2_accounting_trans_commit_revert()` negates and reapplies a committed delta to roll back memory accounting after a failed commit path.

The header ties accounting into transaction commit, GC, device usage initialization/removal, filesystem accounting reads, clean verification, and shutdown.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting_format.h

This header defines the on-disk format for `KEY_TYPE_accounting`.

The key idea is that an accounting key is a `struct disk_accounting_pos`, a type-tagged union overlaid on a `bpos`. Values are variable-length arrays of `u64` counters. Updates written through the write buffer are deltas, and the persistent btree value becomes the accumulated counter state when deltas are flushed or replayed.

The file documents a critical replay invariant: every accounting update receives a unique `bversion` derived from journal position. Journal replay compares journal key version against the btree key version to decide whether a delta still needs replay. Therefore accounting write-buffer flushes must preserve strict temporal ordering, especially while journal replay is active.

Data types:
- `BCH_DATA_free`
- `BCH_DATA_sb`
- `BCH_DATA_journal`
- `BCH_DATA_btree`
- `BCH_DATA_user`
- `BCH_DATA_cached`
- `BCH_DATA_parity`
- `BCH_DATA_stripe`
- `BCH_DATA_need_gc_gens`
- `BCH_DATA_need_discard`
- `BCH_DATA_unstriped`

`data_type_is_empty()` treats free, need-gc-gens, and need-discard as empty states. `data_type_is_hidden()` marks superblock and journal data as hidden from normal capacity accounting.

Accounting types and counter counts:
- `nr_inodes`: 1 counter.
- `persistent_reserved`: 1 counter, keyed by replica count.
- `replicas`: 1 counter, keyed by a replicas entry.
- `dev_data_type`: 3 counters: bucket count, live sectors, fragmented sectors.
- `compression`: 3 counters: extent count, uncompressed size, compressed size.
- `snapshot`: 1 counter.
- `btree`: 3 counters: sectors, nodes, non-leaf nodes.
- `rebalance_work`: 1 counter.
- `inum`: 3 counters: extent count, logical sectors, on-disk sectors.
- `reconcile_work`: 2 counters.
- `dev_leaving`: 1 counter.

The packed structs under `bch_acct_*` define the key fields for each type. `struct disk_accounting_pos` contains the type byte and a packed union of those subtype fields, or the raw `_pad` `bpos` overlay.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting_types.h

This small header defines the in-memory accounting containers.

`struct accounting_mem_entry` stores:
- `pos`: the accounting key position.
- `bversion`: the accounting bkey version.
- `nr_counters`: number of counters for this entry.
- `v[2]`: two per-CPU counter arrays. Index 0 is normal accounting; index 1 is used during GC accounting verification.

`struct bch_accounting_mem` stores:
- `k`: a dynamic array of `accounting_mem_entry`, sorted in Eytzinger order for fast lookup.
- `gc_running`: whether GC comparison counters are allocated and active.

This file is the data-structure companion to `accounting.c` and `accounting.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/background.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/background.c

This file implements persistent alloc-key handling, derived indexes, alloc triggers, capacity calculation, and allocator device state transitions. It also contains extensive documentation for buckets, watermarks, accounting, replicas, backpointers, and allocator consistency.

Alloc format handling:
- Supports legacy alloc v1/v2/v3 unpacking and conversion to `bch_alloc_v4`.
- `bch2_alloc_v1_validate()`, `bch2_alloc_v2_validate()`, `bch2_alloc_v3_validate()`, and `bch2_alloc_v4_validate()` validate alloc key encodings and logical state.
- `bch2_alloc_v4_validate()` checks value size, backpointer layout, data type derivation, io time bounds, and consistency between `data_type` and sector/refcount fields.
- `bch2_alloc_to_v4()` and `bch2_alloc_to_v4_mut()` normalize alloc keys to the current fixed-layout v4 format.

Alloc update helpers:
- `bch2_trans_start_alloc_update_noupdate()` opens an alloc iterator and returns a mutable v4 key without updating it.
- `bch2_trans_start_alloc_update()` opens, mutates, and submits an alloc update in one path.

Bucket generation support:
- `bch2_bucket_gens_validate()` validates packed bucket generation keys.
- `bch2_bucket_gens_to_text()` renders generation arrays.
- `bch2_bucket_gens_init()` builds `BTREE_ID_bucket_gens` from the alloc btree.
- `bch2_alloc_read()` initializes in-memory device bucket generation arrays from `bucket_gens`, or from alloc keys for older metadata versions.

Derived indexes:
- `bch2_bucket_do_freespace_index()` maintains `BTREE_ID_freespace` entries for free buckets.
- `bch2_bucket_do_discard_index()` maintains `BTREE_ID_need_discard` entries through the write buffer.
- `bch2_bucket_gen_update()` updates a packed `bucket_gens` key when an alloc key generation changes.

Device accounting:
- `bch2_dev_data_type_accounting_mod()` submits `dev_data_type` accounting deltas.
- `bch2_alloc_key_to_dev_counters()` compares old/new alloc state and updates per-device bucket, sector, fragmentation, and unstriped counters.

Central trigger:
- `bch2_trigger_alloc()` is the alloc bkey trigger. In transactional mode it normalizes data type, handles nonempty-to-empty transitions as `need_discard`, sets io times, schedules generation increments, repairs suspicious free-state discard bookkeeping, updates freespace/LRU/bucket-gens indexes, reserves journal space for discard index updates, and updates device accounting.
- In atomic mode it records journal sequence transitions, updates in-memory bucket generation arrays, wakes allocators when buckets become free, performs fast discard when safe, updates the need-discard index, starts invalidation for cached buckets under pressure, and schedules async GC-gens work.
- In GC mode it marks GC bucket generation state.

Device removal:
- `bch2_dev_remove_need_discard()` removes need-discard keys for a device.
- `bch2_dev_remove_alloc()` deletes LRU, need-discard, freespace, backpointer, bucket-gens, alloc, and device usage accounting for a removed device.

I/O time and capacity:
- `bch2_bucket_io_time_reset()` updates bucket read/write LRU timestamps.
- `bch2_fs_ra_pages()` computes readahead from online block devices.
- `bch2_recalc_capacity()` computes filesystem capacity, reserved sectors, max bucket size, and wakes allocators.
- `bch2_min_rw_member_capacity()` returns the smallest rw member capacity.

Allocator device state:
- `bch2_dev_allocator_set_rw()` updates allocator device bitmaps by data type, respecting allowed data types and durability.
- `bch2_dev_allocator_remove()` removes a device from allocation, recalculates capacity, stops open buckets, wakes waiters, and waits for in-flight write points.
- `bch2_dev_allocator_add()` adds a device to allocation sets.
- `bch2_fs_allocator_background_init()`, `bch2_fs_capacity_init()`, and `bch2_fs_capacity_exit()` initialize and tear down allocator/capacity state.

Key invariants:
- Alloc `data_type` is derived from sector counts, stripe refcount, discard state, and generation gap.
- Free buckets must be represented in the freespace btree with encoded generation bits.
- Need-discard buckets are indexed by journal sequence and bucket identity.
- Device accounting is derived from alloc key transitions.
- Generation changes must update both persistent `bucket_gens` and in-memory bucket generation arrays.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/background.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/background.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/background.h

This header exposes helpers and declarations for alloc-background logic.

Bucket helpers:
- `bch2_dev_bucket_exists()` validates a `device:bucket` position.
- `bucket_to_u64()` and `u64_to_bucket()` encode/decode bucket positions for btree indexes.

Generation and data type:
- `BUCKET_GC_GEN_MAX` defines the allowed stale generation window.
- `alloc_gc_gen()` computes generation gap.
- `bucket_data_type()` normalizes cached and stripe data as user data from the bucket perspective.
- `bucket_data_type_mismatch()` checks incompatible bucket/pointer data types.
- `data_type_movable()` identifies btree/user/stripe data as movable.

Sector accounting:
- `bch2_bucket_sectors_total()`, `bch2_bucket_sectors_dirty()`, `bch2_bucket_sectors()`, `bch2_bucket_sectors_fragmented()`, and `bch2_bucket_sectors_unstriped()` compute alloc-key sector quantities.
- `alloc_data_type()` derives the logical bucket state.
- `alloc_data_type_set()` stores that derived state.

Auxiliary indexes:
- `alloc_lru_idx_read()` and `alloc_lru_idx_fragmentation()` compute LRU keys.
- `alloc_freespace_genbits()` and `alloc_freespace_pos()` encode generation bits into freespace positions.
- `alloc_gens_pos()`, `bucket_gens_pos_to_alloc()`, and `alloc_gen()` map between alloc keys and packed bucket generation keys.

Alloc v4/backpointer layout:
- `alloc_v4_u64s_noerror()`, `alloc_v4_u64s()`, `set_alloc_v4_u64s()`, `alloc_v4_backpointers()`, and `alloc_v4_backpointers_c()` compute and access alloc v4 variable trailing inline backpointer storage.
- `bkey_is_alloc()` recognizes legacy alloc key types.

The header declares alloc conversion, validation, text rendering, bkey ops, bucket generation initialization, alloc reading, freespace index updates, trigger entry points, device removal, capacity routines, allocator device add/remove/set-rw operations, and capacity lifecycle functions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/background.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/backpointers.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/backpointers.c

This file implements backpointer validation, lookup, insertion/deletion, and recovery checks that verify physical-to-logical references.

Basic operations:
- `bch2_backpointer_validate()` checks backpointer level and rejects `BCH_SB_MEMBER_INVALID` as a normal device.
- `bch2_backpointer_to_text()` renders physical bucket/sector, owner btree/level, data type, suboffset, length, generation, logical position, and flags.
- `bch2_backpointer_swab()` swaps flags, length, and owner position.
- `extent_matches_bp()` recomputes expected backpointers for an extent or btree pointer and compares them with a candidate.

Mutation:
- `bch2_bucket_backpointer_mod_nowritebuffer()` directly inserts or deletes a backpointer, checking for unexpected existing/missing backpointers and scheduling `check_extents_to_backpointers` if needed.
- `bch2_backpointer_del()` deletes through the write buffer or direct btree update depending on the static branch.
- `bch2_backpointers_maybe_flush()` conditionally flushes write-buffered backpointers during validation.

Backpointer resolution:
- `bch2_backpointer_get_key()` and `bch2_backpointer_get_node()` resolve a backpointer to its target extent or btree node.
- `backpointer_target_not_found()` handles mismatches, logs the target and found backpointer, deletes invalid backpointers if fsck allows, and handles write-buffer commit semantics carefully.
- Overwritten btree nodes can be treated as nonfatal in some scan paths.

Recovery passes:
- `bch2_check_btree_backpointers()` verifies every backpointer has a valid alloc bucket.
- `bch2_check_extents_to_backpointers()` first compares bucket sector totals from backpointers against alloc counters, marks buckets with mismatches, then scans owning extents to recreate missing backpointers or resolve duplicates. It supports multi-pass operation when relevant btree nodes do not fit in memory.
- `bch2_check_backpointers_to_extents()` walks backpointer and stripe-backpointer btrees and ensures each backpointer points to an extent/node that still contains the matching pointer. It also supports multi-pass scanning by pinning portions of the owning btrees.

Duplicate and corruption handling:
- `drop_dev_and_update()` removes a device pointer from an extent and converts the key to an error if it becomes unreadable.
- `kill_replica_if_checksum_bad()` reads data or btree nodes, verifies checksums/magic/sequence, and drops a bad replica if corruption proves which duplicate is invalid.
- `check_bp_dup()` handles duplicate physical references, stale pointers, duplicate versions of the same extent, checksum-based repairs, and otherwise reports unimplemented repair for true double allocation.

Scan iterator:
- `bch2_bp_scan_iter_peek()` batches backpointers into memory, sorts them in reverse owner order, tracks write-buffer flushes, and refreshes/deletes entries as flush state changes.
- `backpointer_scan_for_each` in the header drives restart-aware scans.

Bucket mismatch bitmaps:
- `bch2_bucket_bitmap_set()`, `bch2_bucket_bitmap_resize()`, and `bch2_bucket_bitmap_free()` manage per-device bitmaps used to record buckets with missing or empty backpointer sets.

Key invariants:
- Backpointers must match a live extent/btree pointer byte-for-byte after recomputation.
- Backpointer bucket generation filters stale references.
- Alloc bucket sector counters should match the sum of live backpointer lengths by data class.
- Write-buffer races are handled by conditional flushing before repair decisions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/backpointers.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/backpointers.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/backpointers.h

This header defines backpointer helpers, bkey ops, physical/logical position mapping, and scan support.

Bkey operations:
- Declares validation, text, and swab functions.
- `bch2_bkey_ops_backpointer` sets validation, rendering, byte-swap, and minimum value size.

Position conversion:
- `bp_pos_to_bucket()` and `bp_pos_to_bucket_and_offset()` map a backpointer btree position to an alloc bucket and bucket offset.
- `bucket_pos_to_bp_noerror()`, `bucket_pos_to_bp()`, `bucket_pos_to_bp_start()`, and `bucket_pos_to_bp_end()` map a bucket and offset range to backpointer btree positions.
- These conversions use `extent_bp_shift`, so backpointer positions can include a sub-sector discriminator.

Mutation:
- `backpointer_btree()` chooses `BTREE_ID_stripe_backpointers` for stripe pointers and `BTREE_ID_backpointers` otherwise.
- `bch2_bucket_backpointer_mod()` updates reconcile-work bits when needed, optionally bypasses the write buffer, and otherwise inserts/deletes through the buffered update path.

Pointer-to-backpointer construction:
- `bch2_bkey_ptr_data_type()` classifies btree pointers, extents, cached pointers, EC stripe pointers, and stripe data/parity.
- `bch2_extent_ptr_to_bp_pos()` computes the physical backpointer key, including special handling for removed EC devices and stripe backpointers.
- `bch2_extent_ptr_to_bp()` builds a `struct bkey_i_backpointer` from a logical key pointer, filling owner btree, level, data type, generation, physical length, and logical position; it also marks reconcile/EC/stripe flags.

Lookup/check declarations expose functions for resolving backpointers and running integrity checks.

Scan support:
- `struct bp_scan_iter` tracks btree id, current position, flush generation, progress, and a dynamic array of buffered backpointers.
- `DEFINE_CLASS(backpointer_scan_iter)` provides cleanup for scan arrays.
- `backpointer_scan_for_each` is a restart-aware macro that repeatedly peeks, processes, verifies transaction restart count, and advances.

The header also exposes bucket bitmap helpers used by backpointer mismatch recovery.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/backpointers.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets.c

This file implements bucket usage reads, pointer marking, extent/reservation triggers, metadata bucket marking, disk reservations, and bucket memory allocation.

Usage reads:
- `bch2_dev_usage_read_fast()` reads per-data-type bucket counts.
- `bch2_dev_usage_full_read_fast()` reads full per-device per-CPU usage counters.
- `bch2_fs_usage_read_short()` returns capacity, used, and free sectors after hidden usage and reserved-space factors.
- `bch2_dev_usage_to_text()` renders bucket/sectors/fragmented tables.

Pointer validation and repair:
- `bch2_check_fix_ptr()` validates an extent pointer against device existence, bucket validity, GC bucket generation, data type compatibility, and EC stripe metadata. It can mark pointers to drop, stripe metadata to drop, or generations to reset.
- `bch2_no_valid_pointers_repair()` handles extents without valid dirty pointers, converting a good cached pointer to dirty when possible or marking the key with an error.
- `bch2_check_fix_ptrs()` applies pointer repairs to extents during offline/recovery checking. It updates btree roots specially and avoids running on a read-write filesystem.

Bucket reference updates:
- `bch2_bucket_ref_update()` checks pointer generation ordering, stale cached/dirty pointers, data type mismatch, and sector count overflow, then adjusts bucket sector counters. Serious inconsistencies schedule `check_allocations`.

Transaction usage accounting:
- `bch2_trans_account_disk_usage_change()` applies a transaction’s aggregate filesystem usage delta to per-CPU usage counters and consumes disk reservations. It warns if disk usage increased beyond reserved sectors.

Extent triggers:
- `bch2_trigger_pointer()` handles a single decoded extent pointer. In transactional mode it updates the alloc key and backpointer btree; in GC mode it updates GC bucket state and device counters. It handles EC removed-device sentinel pointers and stripe backpointers separately.
- `bch2_trigger_stripe_ptr()` updates stripe block counts and replicas accounting for erasure-coded pointers in both transactional and GC modes.
- `__trigger_extent()` drives all pointers in an extent or btree pointer, updates replicas accounting, snapshot accounting, compression accounting, btree metadata accounting, and per-inode fragmentation accounting.
- `bch2_trigger_extent()` skips work when pointer payloads are unchanged, runs repair mode when requested, sets reconcile needs for new extent inserts, applies overwrite/insert triggers, and invokes reconcile triggers.

Reservation trigger:
- `bch2_trigger_reservation()` accounts `KEY_TYPE_reservation` sectors in `persistent_reserved`, keyed by replica count.

Metadata marking:
- `bch2_trans_mark_metadata_bucket()` marks superblock and journal buckets either transactionally or during GC.
- `bch2_trans_mark_dev_sb()` and `bch2_trans_mark_dev_sbs_flags()` mark all superblock and journal buckets for devices.
- `bch2_is_superblock_bucket()` checks whether a bucket overlaps primary/backup superblock regions or journal buckets.

Disk reservations:
- `__bch2_disk_reservation_add()` and `disk_reservation_recalc_sectors_available()` maintain fast per-CPU reservation caches backed by an atomic global available-sector count.
- Reservation flags support nofail and partial reservations.

Bucket memory lifecycle:
- `bch2_buckets_nouse_alloc()` and `bch2_buckets_nouse_free()` manage bitmaps of buckets unavailable for allocation.
- `bch2_dev_buckets_resize()` allocates/resizes per-device `bucket_gens`, copies old generations, resizes backpointer mismatch bitmaps, and publishes through RCU.
- `bch2_dev_buckets_alloc()` allocates per-device usage counters and bucket generation storage.
- `bch2_dev_buckets_free()` frees bucket generation, no-use bitmap, and usage counters.

Key invariants:
- Extent triggers are the bridge from logical extent changes to alloc counters, backpointers, replicas accounting, compression stats, and inode stats.
- Bucket sector counters must not overflow and must match pointer generation/data type rules.
- Metadata buckets may only be free, superblock, or journal type.
- Disk usage increases must be covered by reservations except for forced correction paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets.h

This header defines bucket addressing, locking, generation access, pointer mapping, usage/reservation helpers, and trigger declarations.

Addressing:
- `sector_to_bucket()`, `bucket_to_sector()`, `bucket_remainder()`, and `sector_to_bucket_and_offset()` convert between sectors and bucket numbers.
- `for_each_bucket` iterates device bucket arrays.

Locking:
- `bucket_lock()` and `bucket_unlock()` implement a compact bit lock on `struct bucket`.
- `DEFINE_GUARD(bucket_lock, ...)` provides scoped locking.

GC bucket and generation access:
- `gc_bucket()` returns an in-memory GC bucket if valid.
- `bucket_gens()`, `bucket_gen()`, `bucket_gen_get_rcu()`, and `bucket_gen_get()` access packed generation arrays.
- `gen_cmp()` and `gen_after()` compare wrapping 8-bit generations.

Pointer mapping:
- `PTR_BUCKET_NR()`, `PTR_BUCKET_POS()`, `PTR_BUCKET_POS_OFFSET()`, and `PTR_GC_BUCKET()` map extent pointers to bucket state.
- `alloc_to_bucket()`, `__bucket_m_to_alloc()`, and `bucket_m_to_alloc()` convert between GC bucket state and alloc v4 state.
- `ptr_data_type()` and `ptr_disk_sectors()` classify pointers and compute compressed on-disk sectors.

Usage and capacity:
- Declares fast/full device usage reads and text rendering.
- `bch2_dev_buckets_reserved()`, `__dev_buckets_free()`, `dev_buckets_free()`, `__dev_buckets_available()`, and `dev_buckets_available()` implement watermark-based availability.
- Declares `bch2_fs_usage_read_short()`.

Trigger and marking declarations:
- Declares `bch2_bucket_ref_update()`, `bch2_check_fix_ptrs()`, extent/reservation triggers, metadata bucket marking, superblock marking, and disk usage accounting.

Disk reservations:
- `bch2_disk_reservation_put()` releases online reserved sectors.
- `bch2_disk_reservation_add()` uses a fast per-CPU path in kernel builds and falls back to the slow path when needed.
- `bch2_disk_reservation_init()` and `bch2_disk_reservation_get()` initialize and acquire reservations.
- A cleanup class releases reservations automatically.
- `RESERVE_FACTOR` and `avail_factor()` account for reservation overhead.

Lifecycle declarations include no-use bitmap management and device bucket allocation/resizing/freeing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets_types.h

This header defines compact bucket and usage data structures.

`BUCKET_LOCK_BITNR` is chosen by byte order so a bit lock fits in the first byte of `struct bucket`. The comments explain this is an intentional space optimization: fsck needs in-memory state for every bucket on every device, and not all architectures support byte-sized `xchg`.

`struct bucket` stores GC/in-memory bucket state:
- one-byte lock
- `gen_valid`
- 7-bit `data_type`
- generation
- dirty, cached, and stripe sector counters

`struct bucket_gens` stores packed per-device generation numbers under RCU, with first bucket, bucket count, and a flexible byte array.

Usage structures:
- `struct bch_dev_usage` stores bucket counts by data type.
- `struct bch_dev_usage_full` stores buckets, compressed sectors, and fragmented sectors for each data type.
- `struct bch_fs_usage_base` stores hidden, btree, data, cached, and reserved filesystem usage.
- `struct bch_fs_usage_short` stores capacity, used, and free.

`struct disk_reservation` records reserved sectors, a generation field, and replica count. These types are consumed by `buckets.c`, `background.c`, and accounting code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/buckets_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/check.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/check.c

This file implements allocator consistency checks and repairs for alloc, freespace, need-discard, bucket-gens, LRU, and stripe references.

Hole synthesis:
- `bch2_get_key_or_hole()` returns either an actual btree key or a synthesized deleted key covering a hole.
- `bch2_get_key_or_real_bucket_hole()` skips invalid device ranges and clips holes to real bucket ranges.
- `next_bucket()` advances through member devices and valid bucket ranges.

Error reporting:
- `bch2_need_discard_or_freespace_err()` reports incorrect presence/absence in the need-discard or freespace btree and can mark errors fixable depending on caller context.

Alloc key checking:
- `bch2_check_alloc_key()` validates one alloc key against:
  - valid device/bucket existence
  - need-discard index presence and journal sequence
  - freespace index presence and generation bits
  - bucket-gens packed generation value
  - stripe refcount from actual stripe references
- It repairs indexes and alloc key fields when fsck policy allows.

Alloc holes:
- `bch2_check_alloc_hole_freespace()` ensures holes in the alloc btree are represented in the freespace btree.
- `bch2_check_alloc_hole_bucket_gens()` ensures bucket-gens entries for alloc holes are zero.

Freespace and discard key checking:
- `__bch2_check_freespace_key()` validates a freespace entry against the corresponding alloc key and generation bits. In async allocator context it queues repair work instead of committing recursively.
- `bch2_check_discard_key()` validates need-discard entries against alloc key data type and `journal_seq_empty`.
- `delete_freespace_key()` supports synchronous or async deletion/repair.
- `check_discard_freespace_key_work()` runs async repair work.

Bucket-gens checking:
- `bch2_check_bucket_gens_key()` removes bucket-gens keys for invalid devices/ranges and zeros generation bytes for invalid buckets outside the usable member range.

Full alloc-info pass:
- `check_btree_alloc()` walks alloc keys and synthesized holes with companion iterators for need-discard, freespace, and bucket-gens.
- `bch2_check_alloc_info()` runs alloc/hole checking, then scans need-discard, freespace, and bucket-gens btrees directly.

LRU and stripe checks:
- `bch2_check_alloc_to_lru_ref()` ensures alloc keys that should have fragmentation or cached-read LRU entries do have them. It repairs cached buckets with zero read time.
- `bch2_check_alloc_to_lru_refs()` walks the alloc btree, checks LRU references, and then calls `bch2_check_stripe_refs()`.

Freespace initialization:
- `dev_freespace_init_iter()` initializes freespace entries from alloc keys or alloc holes.
- `bch2_dev_freespace_init()` scans a device’s bucket range, populates freespace, and marks the member’s freespace initialized flag.
- `bch2_fs_freespace_init()` initializes any member device lacking freespace initialization during mount, except for small-image filesystems, and writes the superblock after completion.

Key invariants:
- Free alloc buckets must appear in the freespace btree with matching generation bits.
- Need-discard alloc buckets must appear in the need-discard btree at a key derived from `journal_seq_empty` and bucket id.
- `bucket_gens` must match alloc key generations for real buckets and be zero for alloc holes/invalid buckets.
- Alloc stripe refcounts must match stripe-tree references.
- Online allocator-path repair avoids recursive allocation commits by using async work.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/check.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/check.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/check.h

This header declares allocator checking and freespace initialization APIs.

It exposes:
- `bch2_need_discard_or_freespace_err()` plus wrapper macros for fsck-style error handling.
- `__bch2_check_freespace_key()` for validating a freespace key, with fsck flags and optional write-buffer flush tracking.
- `bch2_check_freespace_key_async()` as a no-log async repair-oriented wrapper.
- `bch2_check_alloc_info()` for the full alloc/freespace/need-discard/bucket-gens consistency pass.
- `bch2_check_alloc_to_lru_refs()` for alloc-to-LRU and stripe reference checking.
- `bch2_dev_freespace_init()` and `bch2_fs_freespace_init()` for populating freespace indexes for devices or the whole filesystem.

The header is the public interface for the consistency machinery implemented in `alloc/check.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/alloc/check.h -->