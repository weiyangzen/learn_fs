# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_format.h

## Purpose
Defines the on-disk/in-memory packed format for bcachefs extent entries, pointers, checksums, extent flags, btree pointer values, reservations, and inline data.

## Main Interfaces and Behavior
- Extensive documentation explains why checksums live in btree keys instead of adjacent to data: the key establishes what data should be read, so stale or wrong-location data can be detected.
- For trimmed checksummed or compressed extents, CRC entries preserve original compressed/uncompressed size and live offset so reads can fetch/decode the full encoded extent and return only the live subset.
- `BCH_EXTENT_ENTRY_TYPES()` assigns compact entry type IDs for `ptr`, `crc32`, `crc64`, `crc128`, `stripe_ptr`, `rebalance_v1`, `flags`, `reconcile`, and `reconcile_bp`; the type is encoded as the first set bit in the entry word.
- CRC formats scale by space: `bch_extent_crc32` is compact and has no nonce, `crc64` has a 10-bit nonce, and `crc128` has wider sizes/offsets plus full `struct bch_csum`.
- `struct bch_extent_ptr` stores cached/unwritten bits, 44-bit sector offset, 8-bit device id, and 8-bit generation. `struct bch_extent_stripe_ptr` stores EC stripe block, redundancy, and index.
- `struct bch_extent_flags` currently exposes the `poisoned` flag.
- `union bch_extent_entry` overlays all entry layouts and provides endian-aware access to the type word.
- Value layouts include `bch_btree_ptr`, `bch_btree_ptr_v2`, `bch_extent`, `bch_reservation`, and `bch_inline_data`.
- Size macros bound maximum extent and btree-pointer value sizes. They explicitly account for evacuating-device pointers and reconcile placeholder pointers coexisting with normal replicas.

## Dependencies and Coupling
Includes `reconcile/format.h`, so reconcile entries are part of the generic extent-entry union and maximum-size calculations.

## Risks and Invariants
- Bitfield layouts are endian-specific and packed/aligned to 8 bytes.
- Maximum value-size constants are critical allocation bounds used by movement, reconcile, and extent mutation paths.
