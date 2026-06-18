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
