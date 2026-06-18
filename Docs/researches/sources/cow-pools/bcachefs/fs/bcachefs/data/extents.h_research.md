# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents.h

## Role

`extents.h` is the central inline API for bcachefs extent values and other bkeys that contain physical pointers. It abstracts the variable-length extent-entry stream used by data extents, btree pointers, reflink values, stripe keys, reconcile metadata, checksums, and flags.

## Main Interfaces

- Defines entry iteration helpers: `extent_entry_type()`, `extent_entry_u64s()`, `extent_entry_next()`, `bkey_extent_entry_for_each()`.
- Provides typed entry casts for pointers and checksums: `entry_to_ptr()`, `entry_to_crc()`, `to_entry()`.
- Unpacks CRC/compression entries into `struct bch_extent_crc_unpacked` with `bch2_extent_crc_unpack()`.
- Defines pointer iteration APIs over many key types with `bch2_bkey_ptrs_c()`, `bch2_bkey_ptrs()`, `bkey_for_each_ptr()`, and `bkey_for_each_ptr_decode()`.
- Declares validation, text formatting, merge, swab, cut, resize, durability, device membership, pointer drop, and extent-flag helpers.
- Defines bkey operation tables for btree pointers, v2 btree pointers, extents, and reservations.

## Important Behavior

Decoded pointer iteration carries the current CRC entry forward until the next CRC entry, and also records stripe/EC metadata when a `stripe_ptr` precedes a pointer. This matches the on-disk format where checksum/compression metadata applies to following pointers.

The file treats btree pointers, user extents, reflink values, and stripe keys as “keys with pointers” while still preserving key-type-specific layouts. `bch2_bkey_ptrs_c()` is the key dispatch point.

`bch2_key_resize()` preserves extent start position while changing the endpoint, which is important because bcachefs extent bkeys store position as the end of the range.

## Invariants

- Extent entry sizes come from `c->sb.extent_type_u64s`; unknown entries can be skipped only if the superblock advertised their size.
- `extent_entry_drop()` is forbidden for stripe keys because stripe pointer layout is not compatible with generic entry movement.
- Pointer append refuses duplicate devices and enforces `BKEY_EXTENT_VAL_U64s_MAX`.
- Data classification helpers distinguish direct data, inline data, reflink pointers, reservations, allocations, and user data.
- Reconcile/poison flags are represented as extent entries and accessed through generic pointer-entry streams.

## Dependencies

This header depends on `extents_types.h`, bkey APIs, `bch_fs` superblock extent-type metadata, and many implementations in adjacent data/reconcile/trigger code.
