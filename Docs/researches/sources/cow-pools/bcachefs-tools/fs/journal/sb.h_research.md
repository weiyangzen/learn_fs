# File Research: sources/cow-pools/bcachefs-tools/fs/journal/sb.h

This header exposes helpers and field operations for journal superblock fields.

Key responsibilities:
- Defines `bch2_nr_journal_buckets()` for legacy explicit journal bucket arrays.
- Defines `bch2_sb_field_journal_v2_nr_entries()` for compact range entries.
- Declares:
  - `bch_sb_field_ops_journal`
  - `bch_sb_field_ops_journal_v2`
  - `bch2_journal_buckets_to_sb()`
  - `bch2_sb_journal_sort()`

Important invariants:
- Entry counts are derived from `vstruct_end()` and variable-length trailing arrays.
- Null field pointers produce zero entries.

Dependencies:
- Includes superblock I/O and vstruct helpers.

Research notes:
- This header is small but central to journal field parsing by both validator and mutator paths.
