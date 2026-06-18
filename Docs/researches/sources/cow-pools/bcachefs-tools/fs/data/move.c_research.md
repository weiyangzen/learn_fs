# File Research: sources/cow-pools/bcachefs-tools/fs/data/move.c

## Purpose
Implements generic data movement, physical/logical data scans, device and bucket evacuation, scrub operations, journal scrub, repair scheduling, and movement status rendering.

## Main Interfaces and Behavior
- `bch2_data_ops_strs[]` maps ioctl data operation IDs to names.
- Moving context lifecycle:
  - `bch2_moving_ctxt_init()` creates a private transaction, closure, waitqueue, IO lists/counters, rate/stats references, and links the context into `c->moving_context_list`.
  - `bch2_moving_ctxt_exit()` flushes all IO, asserts counters are zero, unlinks, resets the transaction, and zeroes the context.
  - `bch2_moving_ctxt_flush_all()` drains pending reads/writes and waits on the closure.
- Read/write pipeline:
  - `__bch2_move_extent()` allocates a `data_update`, initializes it, starts a read via `__bch2_read_extent()`, and accounts read IO.
  - `move_read_endio()` marks the read done and wakes waiters.
  - `bch2_moving_ctxt_do_pending_writes()` converts completed reads into writes.
  - `move_write_done()` accounts write completion, handles EC allocation failure by marking pending reconcile, exits the data update, and releases closure refs.
- `bch2_move_extent()` handles data extents, btree pointer rewrites, and scrub reads. ENOMEM waits for in-flight IO and restarts.
- `bch2_move_extent_pred()` fetches IO opts, updates reconcile opts, commits lazily, calls a caller-supplied predicate to fill `data_update_opts`, traces the decision, and starts movement when the predicate returns positive.
- `bch2_move_ratelimit()` honors copygc waits, kthread stop/freezer state, configured rate delays, and global in-flight byte/IO limits.
- `bch2_move_data_btree()` walks logical data btrees and btree roots at a level, moving keys selected by a predicate.
- Physical scanning is driven by `struct bp_walk` and `__bch2_move_data_phys()`, which walks either normal device backpointers or EC-orphan stripe backpointers, validates bucket/backpointer mismatches, resolves original keys, and calls movement predicates.
- Evacuation predicates select pointers by device, by removed-device EC stripe association, or by exact bucket/generation. Public helpers include `bch2_evacuate_data()`, `bch2_evacuate_ec_orphan()`, and `bch2_evacuate_bucket()`.
- `scrub_pred()` sets up hard-device reads and skips non-checksummed non-btree data for scrub.
- `bch2_scrub_journal()` walks replayed journal flush ranges newest-first, checks extents referenced by journal keys, records checksum failures by device, updates member flush error counters, and reports a rewind sequence after bad flush ranges.
- `bch2_scrub_journal_do_repairs()` drains queued repair records and self-heals bad replicas through `scrub_journal_repair_one()`.
- `bch2_data_job()` currently dispatches `BCH_DATA_OP_scrub`.
- Text/status helpers render movement counters and in-flight read/write state. Filesystem init/exit manage moving context lists and the journal scrub repair darray.

## Dependencies and Coupling
This file is central glue for allocator/write points, backpointers, btree read/update/interior code, data update, read path, reconcile triggers, EC, journal replay, copygc, and ioctl data jobs.

## Risks and Invariants
- Each in-flight IO holds a closure reference; counters must be balanced before context exit.
- Physical backpointer walks must tolerate write-buffer races and topology changes.
- Movement predicates return positive for “move this key”, zero for skip, and negative for errors; several expected per-extent failures are downgraded so scans continue.
