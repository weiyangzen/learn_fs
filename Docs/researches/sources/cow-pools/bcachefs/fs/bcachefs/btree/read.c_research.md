# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/read.c

This file implements B-tree node read, validation, repair-on-read, read retry, root read, and scrub logic.

Major responsibilities:
- Manages `BTREE_NODE_read_in_flight` and `BTREE_NODE_write_in_flight` wait bits.
- Validates bset headers: metadata version, checksum type, sector offset, magic, btree id, level, sequence, min/max keys, and key format.
- Validates bset keys for size, format, order, key range, value semantics, and compatibility conversions.
- During read completion, walks all written bsets, verifies checksums, decrypts if needed, skips blacklisted journal sequences, and merges sorted keys into a single in-memory bset.
- Drops invalid keys when fsck permits repair and marks nodes needing rewrite.
- Retries failed reads against alternate replicas using `bch2_bkey_pick_read_device()`.
- Logs soft versus hard read errors and schedules rewrite/repair when needed.
- Reads roots synchronously into the B-tree cache.
- Scrubs individual B-tree node replicas by rereading and checksum-validating them, then scheduling rewrite on failure.

Important invariants:
- In-memory loaded nodes are normalized to one sorted bset with rebuilt auxiliary trees.
- `btree_ptr_v2.sectors_written` governs how much node data is expected from disk.
- Updated-range B-tree pointers can cause keys outside the adjusted node bounds to be dropped.
- Write-side validation failure forces emergency read-only rather than silent corruption.

Dependencies include checksum/encryption helpers, extent/device picking, journal sequence blacklist, async object tracking, B-tree sort, locking, update, and recovery error handling.
