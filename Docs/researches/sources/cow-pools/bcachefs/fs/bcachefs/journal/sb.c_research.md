# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/sb.c

## Role

Validates, formats, compacts, and sorts journal bucket superblock fields.

## Major Responsibilities

- Validates legacy `BCH_SB_FIELD_journal` bucket lists for nonzero, in-range, non-duplicate buckets.
- Formats legacy journal bucket lists.
- Validates `journal_v2` compact range entries for positive length, in-range coverage, non-overlap, and `UINT_MAX` total bucket count.
- Formats `journal_v2` ranges.
- Converts an explicit bucket array into compact `journal_v2` ranges with `bch2_journal_buckets_to_sb()`.
- Sorts journal buckets on clean mounts when needed and rewrites the superblock.

## Notable Details

`bch2_journal_buckets_to_sb()` deletes the legacy journal field and writes compact contiguous ranges to `journal_v2`. `bch2_sb_journal_sort()` is only allowed for clean, not-yet-RW filesystems.
