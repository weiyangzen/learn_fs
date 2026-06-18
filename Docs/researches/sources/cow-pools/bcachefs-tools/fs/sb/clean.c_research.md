# File Research: sources/cow-pools/bcachefs-tools/fs/sb/clean.c

This file implements the `BCH_SB_FIELD_clean` superblock section used after clean shutdown.

Purpose:
- Stores btree roots and other journal-like entries in the superblock so a cleanly shut down filesystem can avoid reading/replaying the journal at mount.

Key responsibilities:
- Late-validates clean-section journal entries with `bch2_sb_clean_validate_late()`.
- Finds btree root entries inside either a clean section or a journal set.
- Verifies clean superblock roots against the final journal entry with `bch2_verify_superblock_clean()`.
- Reads and validates a clean section with `bch2_read_superblock_clean()`.
- Appends common journal/superblock entries through `bch2_journal_super_entries_add_common()`.
- Provides superblock field validate/to_text ops.
- Marks the filesystem dirty or clean with `bch2_fs_mark_dirty()` and `bch2_fs_mark_clean()`.

Clean section contents:
- Usage entry for key version.
- Read and write I/O clock entries.
- Btree root journal entries.
- Zero-filled tail padding.

Important behavior:
- If the superblock is marked clean but the clean section is missing, the clean bit is cleared and an invalid clean-section error is returned.
- Verification compares clean-section btree roots against journal roots by presence, level, key size, and key bytes.
- Marking clean sets clean flag, compat bits for allocation info/metadata, resizes the clean field, writes common entries and btree roots, validates, and updates journal position hints.

Important invariants:
- Clean field entries are encoded exactly like journal entries.
- Clean validation checks each entry stays within the superblock field.
- `bch2_fs_mark_clean()` returns early if the superblock is already clean.
- The clean section's journal sequence is the current journal sequence at clean marking.

Dependencies:
- Uses journal validation/text APIs, journal entry construction, btree root serialization, superblock field I/O, fsck error handling, and member journal position helpers.

Research notes:
- This file bridges journal recovery and superblock fast-mount state.
- Clean-section corruption is handled conservatively because it affects whether journal replay can be skipped.
