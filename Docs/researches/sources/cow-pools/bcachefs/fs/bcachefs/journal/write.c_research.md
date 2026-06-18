# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/write.c

This file implements allocation, preparation, checksum/encryption, submission, and completion of journal writes.

Key responsibilities:
- Allocates journal entry replicas on suitable devices, honoring metadata targets and desired replica durability.
- Advances journal devices to fresh buckets when current buckets lack enough free sectors.
- Resizes journal buffers and coordinates write-buffer sizing.
- Compacts journal entries, drops empty reservations, converts `write_buffer_keys`, adds missing B-tree roots, timestamps, common superblock-derived entries, and rewind-limit entries.
- Chooses flush versus noflush journal writes based on errors, explicit flush needs, journal delay, and skip-flush policy.
- Validates journal entries before or after encryption depending on checksum/encryption/version requirements.
- Submits journal bios with flush/FUA semantics and optional separate preflushes for multi-device filesystems.
- Completes writes in sequence order, updates `last_seq_ondisk`, `flushed_seq_ondisk`, `seq_ondisk`, reclaim state, and waiters.
- Handles degraded journal writes and fatal write failure by emergency read-only transition.

Important invariants:
- `journal_buf.write_done` means all post-completion bookkeeping is finished, not just that IO completed.
- Completion must not advance `flushed_seq_ondisk` past a sequence until replica refs for prior sequences are released.
- `j->in_flight.front` is kept equal to `seq_ondisk + 1` for `journal_seq_to_buf()` indexing.
- Clean filesystems defer marking journal replicas until after write completion so a clean superblock is not dirtied before journal data exists.
- `nochganges`/`nochanges` mode skips actual IO but still runs completion bookkeeping.

Dependencies include allocator device targeting, replicas accounting, B-tree root journaling, write-buffer flushing, checksum/encryption, journal reclaim, discard scheduling, superblock clean entries, and block-layer bio submission.
