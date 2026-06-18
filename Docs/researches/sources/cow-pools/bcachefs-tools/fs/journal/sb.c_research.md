# File Research: sources/cow-pools/bcachefs-tools/fs/journal/sb.c

This file implements superblock field operations for journal bucket lists and journal bucket ranges.

Key responsibilities:
- Validates legacy `BCH_SB_FIELD_journal` bucket lists.
- Validates `BCH_SB_FIELD_journal_v2` compact bucket ranges.
- Converts sorted bucket arrays into compact journal v2 superblock ranges with `bch2_journal_buckets_to_sb()`.
- Sorts and rewrites journal superblock fields with `bch2_sb_journal_sort()`.

Validation behavior:
- Legacy journal field validation:
  - Copies buckets into a darray.
  - Sorts them.
  - Rejects sector/bucket zero.
  - Rejects buckets before member `first_bucket`.
  - Rejects buckets beyond member `nbuckets`.
  - Rejects duplicates.
- Journal v2 validation:
  - Expands each entry into a start/end range.
  - Rejects empty or wrapped ranges.
  - Rejects start zero.
  - Rejects ranges before first bucket or past device end.
  - Rejects overlapping ranges.
  - Rejects total bucket count above `UINT_MAX`.

Conversion behavior:
- `bch2_journal_buckets_to_sb()` deletes both journal fields when no buckets remain.
- Non-empty bucket arrays are compacted into contiguous ranges and stored as `journal_v2`.
- Legacy `journal` is deleted when v2 is written.

Important invariants:
- Callers must hold `c->sb_lock` when writing journal buckets to a superblock.
- `bch2_sb_journal_sort()` requires a clean filesystem and not read-write mounted.
- Journal bucket arrays are sorted before v2 compaction during sort/repair.

Dependencies:
- Uses superblock field resize/delete helpers, member lookup, darrays, sort helpers, and online member iteration.

Research notes:
- This file is format-compatibility glue between old explicit bucket lists and newer compact range encoding.
- Validation is device-local: it checks against the superblock member at `sb->dev_idx`.
