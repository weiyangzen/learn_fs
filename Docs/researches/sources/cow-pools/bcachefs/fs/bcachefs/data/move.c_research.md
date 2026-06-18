# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/move.c

## Role

`move.c` is the main data relocation engine. It supports copygc, evacuation, scrub, journal scrub, self-healing repair, and user-visible data jobs by reading existing extents and rewriting or validating them through `data_update`.

## Moving Context

`struct moving_context` tracks in-flight reads and writes, rate limits movement, owns a transaction, and records stats. Reads complete first, then pending writes are started from `bch2_moving_ctxt_do_pending_writes()`.

Key lifecycle:
- `bch2_moving_ctxt_init()` initializes transaction, closure, lists, waitqueue, rate/stats/write point.
- `__bch2_move_extent()` initializes a `data_update`, submits an extent read, and links the operation into context lists.
- `move_read_endio()` marks reads complete and wakes waiters.
- `move_write()` starts data-update write after read completion.
- `move_write_done()` releases accounting and handles EC allocation failures by marking reconcile pending.
- `bch2_moving_ctxt_flush_all()` waits for all reads/writes.
- `bch2_moving_ctxt_exit()` asserts counters drain and removes the context from fs diagnostics.

## Logical and Physical Scans

`bch2_move_data_btree()` walks keys in a logical btree range. It fetches inode/snapshot I/O options, updates reconcile opts if needed, asks a predicate whether to move the key, then calls `bch2_move_extent()`.

`bch2_move_data_phys()` and `__bch2_move_data_phys()` walk physical backpointers. They can scan normal device backpointers or EC-orphan stripe backpointers, resolve each backpointer to the owning key, and move matching extents. The scan also checks bucket/backpointer mismatches.

## Predicates and Operations

- `evacuate_pred()`: kills pointers on a target device.
- `evacuate_ec_orphan_pred()`: matches invalid-device pointers by EC stripe index/block.
- `evacuate_bucket_pred()`: kills noncached pointers in a specific bucket/generation.
- `scrub_pred()`: reads from a required device and scrubs only relevant checksummed extents or btree pointers.

## Journal Scrub

`bch2_scrub_journal()` walks journal flush ranges from newest to older, rereads referenced journal keys from specific devices, detects checksum errors that indicate bad flush/FUA behavior, records device flush errors in member superblock fields, and returns a rewind sequence.

`bch2_scrub_journal_do_repairs()` drains queued bad-replica repairs and rewrites affected extents with self-heal options.

## User Job Entry

`bch2_data_job()` currently handles scrub jobs, initializes stats, flushes btree interior updates, and calls physical movement with `scrub_pred()`.

## Diagnostics

`bch2_move_stats_to_text()` and `bch2_fs_moving_ctxts_to_text()` print progress, counters, limits, and in-flight data updates.

## Invariants

- Movement I/O is throttled by both sectors and I/O counts.
- Memory allocation failures are handled by waiting for I/O progress and returning nested transaction restart.
- Data update failures for individual extents are tolerated for long scans.
- EC allocation failures during movement turn into pending reconcile work rather than disappearing.
