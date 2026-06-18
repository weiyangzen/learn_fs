# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/debug.c

General bcachefs debug and debugfs implementation. Provides btree dumps, transaction diagnostics, journal pin reporting, write-point reporting, node-scan reporting, and on-disk btree node rendering.

Key entry points:
- `bch2_btree_node_ondisk_to_text()` reads a btree node from its selected device, verifies checksums, decrypts bsets, and prints packed keys as stored on disk.
- `bch2_debugfs_flush_buf()` streams `printbuf` contents to userspace while preserving partially flushed data.
- `bch2_dump_open()` and `bch2_dump_release()` allocate/free `dump_iter` state for most debugfs files.
- `bch2_read_btree()`, `bch2_read_btree_formats()`, and `bch2_read_bfloat_failed()` dump btree keys, btree node formats, and bfloat diagnostics.
- `bch2_cached_btree_nodes_read()` dumps cached btree nodes from the rhashtable.
- `bch2_btree_transactions_read()`, `btree_transaction_stats_read()`, and `btree_deadlock_to_text()` expose live transaction state, stats, backtraces, and deadlock checks.
- `bch2_journal_pins_read()`, `bch2_btree_updates_read()`, `bch2_write_points_read()`, and `bch2_btree_node_scan_read()` expose journal pins, pending btree updates, allocator write points, and discovered node-scan entries.
- `bch2_fs_debug_init()` creates per-filesystem debugfs files/directories, including async object debugfs and per-btree subdirectories.
- `bch2_debug_init()`, `bch2_debug_exit()`, and `bch2_fs_debug_exit()` manage global and per-filesystem debugfs roots.

Important invariants:
- Most btree debug reads return nothing until `BCH_FS_may_go_rw` because multithreaded btree access is unsafe while journal-key gap-buffer recovery is still mutating state.
- Long debugfs reads preserve cursor state in `dump_iter` and repeatedly flush to avoid unbounded userspace copies.
- Live transaction traversal uses SRCU, `seqmutex`, sorted pointer order, and refcount checks to survive concurrent transaction changes.
- On-disk btree rendering validates checksum type and checksum before decrypting/printing each bset.
- Debugfs initialization tolerates missing/failed debugfs dentries by returning early.

Dependencies and interactions:
- Uses btree cache/iter/locking/read/update/node-scan helpers, extent read-device selection, journal reclaim/pin reporting, data update text helpers, async object debugfs, inode/fs init state, Linux debugfs, seq files, and bio submission.
