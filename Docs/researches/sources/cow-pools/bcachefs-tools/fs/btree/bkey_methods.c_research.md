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
