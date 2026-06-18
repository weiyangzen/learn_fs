# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/backpointers.c

This file implements backpointer validation, lookup, update, bidirectional consistency checking, and repair.

Basic operations:
- Validates `KEY_TYPE_backpointer` values for legal btree level and non-invalid device.
- Formats backpointers with bucket, offset, owner btree/level, data type, length, generation, and flags.
- Byte-swaps backpointer values.
- `extent_matches_bp()` regenerates expected backpointers for all decoded pointers in a target key and compares them with a stored backpointer.

Backpointer updates:
- `bch2_bucket_backpointer_mod_nowritebuffer()` performs direct insert/delete with consistency checks.
- Normal updates go through the write-buffer path defined in `backpointers.h`.
- Insert/delete anomalies schedule `check_extents_to_backpointers` unless that recovery pass is already planned.

Lookup:
- `bch2_backpointer_get_key()` and `bch2_backpointer_get_node()` resolve a backpointer to the extent or btree node it references.
- Missing or mismatched targets are handled by `backpointer_target_not_found()`, which can delete stale backpointers and accounts for write-buffer races.

Recovery passes:
- `bch2_check_btree_backpointers()` verifies every backpointer has a valid device and alloc key.
- `bch2_check_extents_to_backpointers()` first compares bucket sector totals from backpointers with alloc counters, marks mismatching buckets, then scans relevant extent/btree data to recreate or fix missing backpointers.
- `bch2_check_backpointers_to_extents()` scans backpointers and verifies each resolves to a matching extent or btree node, pinning chunks of btree nodes when the full set cannot fit in memory.

Repair behavior:
- Missing backpointers can be inserted.
- Stale backpointers can be deleted.
- Duplicate backpointers are analyzed by resolving the other owner. If one owner has a stale device pointer, it is dropped.
- If two leaf extents reference overlapping physical space and both checksums verify, the overlapping region can be converted to a shared reflink representation instead of discarding data.
- If checksum verification shows one duplicate physical reference is bad, that replica is dropped.
- Some duplicate non-leaf or otherwise unhandled cases return `fsck_repair_unimplemented`.

Performance and memory:
- Bucket mismatch bitmaps avoid full bidirectional scans when backpointer sector counts match alloc counters.
- The scanner batches backpointers into memory, sorts by owner position in reverse order, and refreshes buffered entries after write-buffer flushes.
- Multi-pass scans are used when the btree nodes needed for verification exceed the configured fsck memory budget.
