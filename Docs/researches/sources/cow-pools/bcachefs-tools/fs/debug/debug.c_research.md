# File Research: sources/cow-pools/bcachefs-tools/fs/debug/debug.c

## Role

Implements assorted bcachefs debug and debugfs support. It can dump on-disk btree nodes, expose live btree keys and formats, show cached btree nodes, active transactions, journal pins, pending btree updates, transaction stats, deadlock diagnostics, btree node-scan results, write-point state, and async object lists.

## On-Disk Btree Node Dumping

`bch2_btree_node_ondisk_to_text()` selects a readable device for a btree node, obtains a read IO reference, reads the node directly from disk, verifies bset checksum(s), decrypts bsets in place via `bset_encrypt()`, and prints each packed key after disassembly. It reports invalid devices, offline devices, allocation failures, IO errors, unknown checksum types, and checksum failures.

## Shared Debugfs Iteration

`struct dump_iter` is allocated by open helpers and carries filesystem/list/btree identity, iterator positions, user buffer, size, copied byte count, and a `printbuf`.

`bch2_debugfs_flush_buf()` copies buffered text to userspace, updates `dump_iter` state, shifts remaining buffer contents down, fixes printbuf newline/field offsets, and returns either more-room status or bytes copied.

`bch2_dump_release()` frees the printbuf and iterator.

## Btree Debug Files

Per-btree debugfs directories contain:

- `keys`: `bch2_read_btree()` walks btree keys with prefetch and all snapshots, prints each key, advances `from`, and flushes as it goes.
- `formats`: `bch2_read_btree_formats()` walks btree nodes by level and prints node formatting/state text.
- `bfloat-failed`: `bch2_read_bfloat_failed()` prints nodes and failed bfloat conversion details.

All btree readers return no content until `BCH_FS_may_go_rw` is set, avoiding unsafe concurrent btree access during early recovery/journal gap-buffer mutation.

## Cache and Transaction Diagnostics

`bch2_cached_btree_nodes_read()` RCU-walks the btree cache rhashtable bucket by bucket and prints cached node address, btree id/level, key, flags, read-lock state, write-blocked state, reachability state, journal pins, and open buckets.

`bch2_btree_transactions_read()` SRCU/seqmutex-walks active btree transactions, sorts the transaction list by pointer, safely obtains transaction refs, prints transaction state and task backtrace, and handles relock restarts.

`btree_transaction_stats_read()` prints per-transaction-function memory, duration, optional kmalloc traces, lock hold/wait time stats, and max allocated path text.

`btree_deadlock_to_text()` walks live transactions until `bch2_check_for_deadlock()` finds and prints a deadlock.

## Journal, Updates, Node Scan, and Write Points

- `bch2_journal_pins_read()` streams journal sequence pin information.
- `bch2_btree_updates_read()` prints current btree update state once per open iterator.
- `bch2_btree_node_scan_read()` prints found btree nodes from the node-scan structure in inorder-to-Eytzinger order under the node-scan mutex.
- `bch2_write_points_read()` prints allocator write-point state via `bch2_write_points_to_text()`.

## Debugfs Tree Lifecycle

`bch2_debug_init()` creates the global `/sys/kernel/debug/bcachefs` root. `bch2_debug_exit()` removes it.

`bch2_fs_debug_init()` creates a per-filesystem directory named by UUID for multidevice filesystems or by filesystem name otherwise. It creates top-level files for cached nodes, transactions, journal pins, btree updates, transaction stats, deadlock, node scan, write points, and async objects. It then creates a `btrees` directory and per-btree debug subdirectories.

`bch2_fs_debug_exit()` removes the per-filesystem debugfs tree.
