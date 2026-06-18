# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/trigger.h

## Role

`reconcile/trigger.h` declares reconcile trigger APIs and provides mapping helpers for reconcile work positions and option caching.

## Position Mapping

- `data_to_rb_work_pos()`: maps extents, reflink, and stripes into the shared reconcile work namespace.
- `rb_work_to_data_pos()`: reverses that mapping into a `bbpos`.
- `rb_work_id()`: maps a reconcile entry to none, pending, hipri, or normal.
- `rb_work_id_phys()`: suppresses pending for physical work tracking.

## Utility Helpers

- `io_opts_to_reconcile_opts()`: converts inode I/O options into an extent reconcile entry.
- `rb_bp()`: constructs a btree-node reconcile backpointer payload.
- `extent_has_rotational()`: checks whether any pointer references a rotational device.
- `rb_needs_trigger()`: true when reconcile entry needs trigger side effects.

## Declared APIs

- validation/text: `bch2_extent_reconcile_validate()`, `bch2_extent_rebalance_v1_to_text()`, `bch2_extent_reconcile_to_text()`
- reconcile lookup/work id: `bch2_bkey_reconcile_opts()`, `bch2_bkey_reconcile_work_id()`
- backpointer management: `bch2_bkey_get_reconcile_bp_pos()`, `bch2_bkey_set_reconcile_bp()`, `reconcile_bp_add()`, `reconcile_bp_del()`, `reconcile_bp_get_key()`
- trigger/update: `__bch2_trigger_extent_reconcile()`, `bch2_trigger_extent_reconcile()`, `bch2_update_reconcile_opts()`, `bch2_bkey_set_needs_reconcile()`, `bch2_extent_trigger_set_needs_reconcile()`
- option lookup: `bch2_bkey_get_io_opts()`

## Snapshot Option Cache

`struct per_snapshot_io_opts` caches filesystem and inode options while scanning keys. It tracks current inode, metadata/user mode, scan-cookie cache bits, per-device cookie cache, and a dynamic array of snapshot-specific inode options.
