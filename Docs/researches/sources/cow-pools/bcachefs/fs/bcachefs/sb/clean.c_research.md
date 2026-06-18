# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/clean.c

This file implements the `BCH_SB_FIELD_clean` superblock section used after clean shutdown.

Key responsibilities:
- Validates clean-section journal-entry-shaped records, including late validation through journal entry validators.
- Reads and duplicates the clean section from the superblock when a filesystem is marked clean.
- Verifies that clean-section journal sequence and B-tree roots match the actual journal after clean shutdown.
- Adds common superblock/journal entries for key version and IO clocks.
- Renders clean-section flags, journal sequence, and contained journal entries.
- Marks filesystems dirty by clearing the clean bit and ensuring always-on features.
- Marks filesystems clean by resizing/populating the clean section with common entries and current B-tree roots, validating it, and recording journal member positions.

Important invariants:
- The clean section stores entries in the same format as journal entries.
- If the superblock says clean but no clean section exists, the clean bit is cleared and an invalid-clean error is returned.
- Clean-section entry bounds are validated both structurally and with the same bkey/journal validation machinery used by the journal.
- Clean shutdown captures all B-tree roots so the next mount can skip journal replay.
