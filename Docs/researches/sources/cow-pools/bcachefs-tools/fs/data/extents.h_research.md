# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents.h

## Purpose
Core header for generic bcachefs keys that carry extent pointers. It defines entry traversal, CRC unpacking, pointer iteration/decoding, key classification helpers, durability/device queries, pointer mutation helpers, bkey ops declarations, and generic extent cutting/resizing helpers.

## Main Interfaces and Behavior
- Extent-entry access uses `extent_entry_type()`, `extent_entry_u64s()`, `extent_entry_bytes()`, `extent_entry_next()`, and `extent_entry_next_safe()`. Runtime entry sizes come from `c->sb.extent_type_u64s`, which lets newer entry layouts be skipped by older tools when known through the superblock.
- `__extent_entry_insert()` and `extent_entry_drop()` physically insert/remove variable-sized entries inside a bkey value and adjust `k->k.u64s`. `extent_entry_drop()` rejects `KEY_TYPE_stripe` because stripe pointer layout is not compatible with the generic memmove path.
- Type helpers distinguish pointer, stripe pointer, and CRC entries. `bch2_extent_crc_unpack()` converts on-disk `crc32`, `crc64`, and `crc128` entries into `struct bch_extent_crc_unpacked`, defaulting to an unencoded full-key extent when no CRC entry applies.
- `bch2_bkey_ptrs_c()` returns the pointer-entry span for btree pointers, extents, stripes, reflink values, and v2 btree pointers. Non-pointer-bearing key types return `{ NULL, NULL }`.
- The macro family `bkey_extent_entry_for_each*`, `bkey_for_each_ptr*`, `bkey_for_each_ptr_decode*`, and `bkey_for_each_crc*` is the canonical way to walk interleaved CRC/stripe/pointer entries. The decoded iterator carries the currently active CRC and EC association for each pointer.
- Defines bkey ops macros for `btree_ptr`, `btree_ptr_v2`, `extent`, and `reservation`, wiring validation, text rendering, endian swabbing, triggers, merge, compat, and repair hooks.
- Classification helpers include `bkey_is_btree_ptr()`, `bkey_extent_is_direct_data()`, `bkey_is_user_data()`, `bkey_extent_is_inline_data()`, `bkey_extent_is_data()`, `bkey_extent_is_allocation()`, `bkey_extent_is_unwritten()`, and `bkey_extent_is_reservation()`.
- Device/durability surface includes declarations for pointer counts, compression sectors, replicas, per-device durability, key durability, readability, device membership, target membership, stale/extra durability dropping, and text/validation routines.
- Mutation helpers append pointers, append decoded pointers, drop pointers/devices/EC masks, match extents and pointers, set cached state, and manage extent flags. The `bch2_bkey_drop_ptrs*` macros deliberately restart iteration after each removal because entry addresses shift.
- Generic extent helpers classify overlap, cut front/back, resize while preserving start offset, and read/set extent flags stored in an optional `flags` entry.

## Dependencies and Coupling
This header is heavily coupled to `bcachefs_format.h` key types through `bkey_s_*` conversions and to reconcile through entry types declared in `extents_format.h`. Many operations assume a visible `struct bch_fs *c` variable in iterator macros, which is an important call-site convention.

## Risks and Invariants
- `extent_entry_u64s()` BUGs if an entry type is at or above `c->sb.extent_types_known`; callers must use safe iteration when parsing possibly unknown data.
- Pointer decoding relies on CRC entries applying to all following pointers until the next CRC entry.
- Append/drop helpers assume caller-provided buffers are large enough; several paths enforce `BKEY_EXTENT_VAL_U64s_MAX` or explicit buffer u64 capacities.
