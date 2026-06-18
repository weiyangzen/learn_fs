# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/check.c

## Purpose
Fsck/checker support for reconcile metadata. It verifies and repairs reconcile work btrees, physical reconcile work, btree-node reconcile backpointers, reconcile-scan backpointers, and stripe widening metadata.

## Main Interfaces and Behavior
- `fix_reconcile_work_btree()` sets or clears a bit in a reconcile work btree depending on whether that btree is the desired location.
- `check_reconcile_work_one()` parallel-walks a data btree and the normal/hipri/pending reconcile work btrees, maps data positions to reconcile work positions, computes where a key should be queued via `bch2_bkey_reconcile_work_id()`, repairs mismatches, and refreshes reconcile options.
- `check_reconcile_work_data_btree()` applies the above to a full data btree with progress and write-buffer flush tracking.
- `check_reconcile_work_phys_one()` validates physical reconcile work btrees against backpointer `BACKPOINTER_RECONCILE_PHYS()` state.
- `check_reconcile_work_phys()` scans normal backpointers and physical reconcile work/hipri btrees.
- `check_reconcile_work_btree_key()` refreshes reconcile opts on btree pointer keys and validates/repairs their `reconcile_bp` extent entries and corresponding `BTREE_ID_reconcile_scan` backpointer records.
- `check_reconcile_work_btrees()` walks all live btree roots and interior nodes by level to validate btree pointer reconcile state.
- `check_reconcile_btree_bp()` and `check_reconcile_btree_bps()` validate reconcile scan backpointers by resolving them back to btree node keys.
- `check_stripe_can_widen_one()` recomputes each stripe’s `can_widen` from disk label RW-member count and EC policy; it skips errors if a stripe scan cookie is already pending.
- `check_stripe_can_widen()` scans stripes with a widen cache.
- `bch2_check_reconcile_work()` orchestrates checks over stripes, reflink, extents, physical reconcile work, btrees, reconcile backpointers, and stripe widening.

## Dependencies and Coupling
Depends on reconcile trigger/work helpers, btree bit btrees, write-buffer flush state, EC stripe widen helpers, progress indicators, and fsck error machinery.

## Risks and Invariants
- Data positions are remapped into shared reconcile work keyspace; stripes/reflink/extents occupy different ranges through `data_to_rb_work_pos()`.
- The checker repairs by mutating bit btrees and btree-node keys; transaction restarts and commits are intentionally frequent.
