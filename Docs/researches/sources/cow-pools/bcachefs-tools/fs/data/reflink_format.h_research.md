# File Research: sources/cow-pools/bcachefs-tools/fs/data/reflink_format.h

## Role

Defines the on-disk value formats for bcachefs reflink pointers and indirect data.

## Structures

`struct bch_reflink_p` contains:

- Base `struct bch_val`.
- `idx_flags`, a 64-bit field split into a 56-bit indirect index plus flags.
- `front_pad` and `back_pad`, used to remember the full indirect range referenced when a pointer covers only part of an indirect extent that may later be split.

`struct bch_reflink_v` contains:

- Base value.
- 64-bit little-endian refcount.
- Flexible extent-entry storage beginning at `start[0]`.

`struct bch_indirect_inline_data` contains:

- Base value.
- 64-bit little-endian refcount.
- Inline data bytes.

## Bitfields

`REFLINK_P_IDX` covers bits 0-55. `REFLINK_P_ERROR` is bit 56 and marks a pointer whose live indirect data is missing. `REFLINK_P_MAY_UPDATE_OPTIONS` is bit 57 and allows reconcile to propagate IO path options from the referencing inode to indirect data.
