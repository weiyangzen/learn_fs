# File Research: sources/cow-pools/bcachefs-tools/fs/fs/dirent_format.h

## Purpose

Defines the on-disk/in-btree dirent value format.

## Format

`struct bch_dirent` contains:

- Base `struct bch_val`.
- Target union:
  - `d_inum` for ordinary entries.
  - `d_child_subvol` and `d_parent_subvol` for `DT_SUBVOL`.
- Bitfield byte with `d_type`, unused bits, and `d_casefold`.
- Name payload:
  - Plain flexible `d_name[]`, or
  - Packed casefold block with original length, casefolded length, and concatenated names.

Constants:

- `DT_SUBVOL = 16`.
- `BCH_DT_MAX = 17`.
- `BCH_NAME_MAX = 512`.

## Notes

The comments explain that dirents and xattrs are indexed by 64-bit string hashes in key offsets with linear probing. Deletions may require whiteouts to preserve probe chains and stable readdir cookies.
