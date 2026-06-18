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
