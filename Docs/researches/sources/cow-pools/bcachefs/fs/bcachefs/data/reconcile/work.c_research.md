# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/work.c

Background reconcile worker implementation for bcachefs. It converts scan cookies and reconcile work btree entries into move-path data updates, stripe repairs, option propagation scans, and pending retries.

Key entry points:
- `bch2_set_reconcile_needs_scan_trans()`, `bch2_set_reconcile_needs_scan()`, `bch2_set_fs_needs_reconcile()` enqueue scan cookies in `BTREE_ID_reconcile_scan`.
- `bch2_set_reconcile_needs_scan_pre()` and `bch2_set_reconcile_needs_scan_post()` bracket option changes with in-flight scan-cookie registration so a scan that overlaps an incomplete option change cannot clear the cookie.
- `bch2_extent_reconcile_pending_mod()` toggles the embedded reconcile `pending` bit for extents or btree nodes.
- `bch2_reconcile_start()`, `bch2_reconcile_stop()`, `bch2_fs_reconcile_init()`, and `bch2_fs_reconcile_exit()` manage the reconcile kthread, rhashtable state, and optional power notifier.
- `bch2_reconcile_status_to_text()` and `bch2_reconcile_scan_pending_to_text()` expose runtime state for status/debug output.

Core flow:
- Scan cookies encode filesystem-wide, metadata-only, pending, stripes, device, or inode scans. Scans update reconcile option state by walking btrees, backpointers, stripe keys, or a single inode’s extents.
- `reconcile_set_data_opts()` derives `data_update_opts` from an extent’s `bch_extent_reconcile` entry: target, checksum, compression, replica changes, EC add/drop, pointer kill masks, and flags such as `BCH_WRITE_must_ec`.
- Direct extents are processed through `bch2_move_extent()`. Stripe keys go through `bch2_stripe_repair()`. Btree-node reconcile work is reached through backpointers.
- Work phases run in fixed order: scan cookies, high-priority btree work, high-priority physical work, high-priority logical work, normal btree/physical/logical work, then pending work.
- Rotational physical work is fanned out per online rotational device so `reconcile_*_phys` work is consumed in device LBA order.

Important invariants:
- In-flight option-change scan cookies must not be deleted by the reconcile thread.
- Pending work is skipped unless a pending scan cookie was seen during the pass.
- Transaction restarts are either handled locally or treated as fatal in paths where they should have been suppressed.
- Reconcile only runs when mounted writable, `reconcile_enabled` is set, and AC-only policy permits it.
- EC stripe retries wait until older move IO has drained before retrying block evacuation work.

Dependencies and interactions:
- Uses btree iterators/update, write buffer flushing, moving context, data update/write, copygc, EC stripe repair, backpointer lookup, inode option lookup, reflink option propagation, progress reporting, power-supply notifications, and trace events.
