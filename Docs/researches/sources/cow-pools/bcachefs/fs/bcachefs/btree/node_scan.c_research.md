# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan.c

This file implements recovery-time scanning for B-tree nodes on disk. It is used when normal topology or roots cannot fully recover a B-tree and the filesystem must discover valid node replicas directly from member devices.

Key flow:
- Worker threads scan devices that allow B-tree data, using the device B-tree bitmap when available.
- `try_read_btree_node()` reads candidate node headers, checks magic, decrypts enough header fields if needed, validates btree id/level bounds, then reads the full node and calls `bch2_btree_node_read_done()`.
- Found nodes are stored as `found_btree_node` records with btree id, level, sequence, journal sequence, cookie, key range, sectors written, and replica pointers.
- `bch2_scan_for_btree_nodes()` merges replicas by cookie, sorts by position, and resolves overwritten ranges by comparing node sequence/journal time.
- Final nodes are Eytzinger-sorted for range lookup.
- `bch2_get_scanned_nodes()` converts scanned nodes back into btree pointer keys and inserts them into the journal overlay for recovery.

Important invariants:
- Duplicate replicas are grouped by node cookie.
- Overlapping nodes at the same btree/level are trimmed or discarded using recency.
- Big-endian scanned nodes are rejected because this path cannot perform full endian conversion.
- Only btrees marked recoverable-from-scan are exposed through `bch2_get_scanned_nodes()`.

Dependencies include bucket generation lookup, B-tree read validation, journal overlay insertion, recovery passes, kthreads, and heap/sort helpers.
