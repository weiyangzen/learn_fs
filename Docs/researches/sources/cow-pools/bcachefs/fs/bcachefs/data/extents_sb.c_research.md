# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents_sb.c

## Role

`extents_sb.c` implements the superblock field that records the size, in u64s, of each extent entry type. This supports forward-compatible parsing of extent streams containing newer entry types.

## Main Functions

- `extent_entry_u64s_known()`: returns the in-memory known size for every compiled-in `BCH_EXTENT_ENTRY_*` type.
- `bch2_sb_extent_type_u64s_to_cpu()`: loads advertised entry sizes from the superblock into `c->sb.extent_type_u64s` and sets `extent_types_known`.
- `bch2_sb_extent_type_u64s_from_cpu()`: allocates/fills the superblock field from the compiled-in entry-size table.
- `bch2_sb_extent_type_u64s_validate()`: verifies superblock-advertised sizes match compiled-in sizes for known entry types.
- `bch2_sb_extent_type_u64s_to_text()`: prints entry names and sizes.
- `bch_sb_field_ops_extent_type_u64s`: registers validate/text callbacks.

## Important Behavior

Even after reading the superblock field, the implementation overwrites all compiled-in entry sizes with `extent_entry_u64s_known()` and ensures `extent_types_known >= BCH_EXTENT_ENTRY_MAX`. Older or newer fields are only useful for parsing beyond what the current binary knows.

## Invariants

- Validation rejects mismatches for any known extent entry type.
- `from_cpu()` requires `c->sb_lock`.
- Missing allocation for the superblock field becomes `ENOSPC_sb_extent_type_u64s`.
