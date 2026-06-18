# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_format.h

## Role

`extents_format.h` defines the on-disk layout for bcachefs extent entries, btree pointers, reservations, and inline data. It also documents why bcachefs stores checksums in btree metadata rather than next to the data blocks.

## On-Disk Model

Extent values are streams of typed entries. Entry type is encoded by the position of the first set bit, allowing compact discrimination between entries such as pointers, CRCs, stripe pointers, reconcile metadata, and flags.

Checksum entries apply to following pointers until superseded by another checksum entry. This allows multiple replicas of the same logical extent to have different physical formats after copygc, tiering, promotion, or partial overwrites.

## Main Structures

- `struct bch_extent_crc32`, `bch_extent_crc64`, `bch_extent_crc128`: packed CRC/compression descriptors with biased size fields.
- `struct bch_extent_ptr`: physical device pointer with cached/unwritten bits, 44-bit offset, device id, and generation.
- `struct bch_extent_stripe_ptr`: EC stripe association.
- `struct bch_extent_flags`: per-extent flags, currently including `poisoned`.
- `union bch_extent_entry`: generic typed entry union.
- `struct bch_btree_ptr`, `bch_btree_ptr_v2`: btree node pointer payloads.
- `struct bch_extent`: generic user/reflink extent payload.
- `struct bch_reservation`: reservation/unwritten allocation metadata.
- `struct bch_inline_data`: inline data payload.

## Size Limits

The file defines maximum key/value sizes for extent and btree pointer values:
- `BKEY_EXTENT_PTR_U64s_MAX`
- `BKEY_EXTENT_VAL_U64s_MAX`
- `BKEY_EXTENT_U64s_MAX`
- `BKEY_BTREE_PTR_VAL_U64s_MAX`
- `BKEY_BTREE_PTR_U64s_MAX`

These limits account for maximum replicas, evacuating-device pointers, reconcile placeholder pointers, and reconcile backpointer metadata.

## Important Design Point

For checksummed or compressed extents, partial overwrites cannot simply move the physical pointer forward. Reads must fetch the full original encoded extent, verify/decompress it, then return the live portion. The CRC entry records original compressed/uncompressed sizes and the live offset.
