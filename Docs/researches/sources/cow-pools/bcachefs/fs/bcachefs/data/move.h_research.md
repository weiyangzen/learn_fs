# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/move.h

## Role

`move.h` declares the data movement API and defines `struct moving_context`.

## Main Types and APIs

- `struct moving_context`: transaction, stats, rate limit, write point, in-flight read/write lists, counters, closure, waitqueue.
- `move_pred_fn`: predicate used by movement scans to decide whether and how a key should be updated.
- Movement lifecycle: `bch2_moving_ctxt_init()`, `bch2_moving_ctxt_exit()`, `bch2_moving_ctxt_flush_all()`.
- Movement operations: `bch2_move_extent()`, `bch2_move_data_btree()`, `bch2_move_data_phys()`, `bch2_evacuate_data()`, `bch2_evacuate_ec_orphan()`, `bch2_evacuate_bucket()`.
- Scrub and jobs: `bch2_scrub_journal()`, `bch2_scrub_journal_do_repairs()`, `bch2_data_job()`.
- Stats/diagnostics and fs init/exit helpers.

## Wait Macros

`move_ctxt_wait_event()` and `move_ctxt_wait_event_timeout()` always process pending writes before sleeping and unlock the long-held transaction while blocked.

## Invariants

Every in-flight operation holds a closure reference; context flush/exit waits for all references and asserts all counters are zero.
