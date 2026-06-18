# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_sb.c

## Purpose
Implements the superblock field that records extent-entry sizes in u64s. This lets code parse extents containing entry types from newer versions by knowing their serialized length.

## Main Interfaces and Behavior
- `extent_entry_u64s_known()` maps each known `BCH_EXTENT_ENTRY_*` type to `sizeof(struct bch_extent_*) / sizeof(u64)`.
- `bch2_sb_extent_type_u64s_nr_entries()` computes the number of stored byte entries in the variable-sized superblock field.
- `bch2_sb_extent_type_u64s_to_cpu()` reads the superblock field into `c->sb.extent_type_u64s` and `extent_types_known`, then overwrites all currently known entries with compiled-in sizes and ensures at least `BCH_EXTENT_ENTRY_MAX` known entries.
- `bch2_sb_extent_type_u64s_from_cpu()` allocates/min-sizes the superblock field under `c->sb_lock` and writes compiled-in sizes.
- Validation checks stored sizes against compiled-in known sizes and reports `invalid_sb_extent_type_u64s` on mismatch.
- Text rendering prints each recorded entry type name, or an unknown type label, with its u64 size.

## Dependencies and Coupling
Uses `data/extents_sb.h`, superblock field helpers from `sb/io.h`, and `bch2_extent_entry_types[]`.

## Risks and Invariants
- Known entry sizes must match compiled structures exactly; a mismatch indicates incompatible/corrupt superblock metadata.
- The `to_cpu()` function currently writes compiled sizes for all known entries regardless of what was read, while preserving the maximum known count.
