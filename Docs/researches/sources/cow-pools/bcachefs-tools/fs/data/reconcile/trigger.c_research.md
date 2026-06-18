# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/trigger.c

## Purpose
Implements validation, text rendering, extraction, trigger accounting, work-btree updates, btree reconcile backpointer management, IO option lookup, and mutation of extent reconcile metadata.

## Main Interfaces and Behavior
- `bch2_extent_reconcile_validate()` rejects pending without need, hipri without data-replicas work, and zero data replicas.
- `bch2_bkey_reconcile_opts()` finds a reconcile entry among a key’s extent entries. `bch2_bkey_reconcile_work_id()` maps stripe `needs_reconcile` or extent reconcile bits to a work ID.
- Text renderers output v1 rebalance or current reconcile options, including inode-derived markers and targets.
- `rb_accounting_counters()` converts a reconcile entry to accounting counters, adding pending/high-priority accounting and suppressing target/replica counters while pending.
- Reconcile backpointer helpers:
  - `bch2_bkey_get_reconcile_bp_pos()` returns `(work_id, bp_index)`.
  - `bch2_bkey_set_reconcile_bp()` adds, updates, or drops the `reconcile_bp` entry in a key.
  - `reconcile_bp_add()` allocates a backpointer record in `BTREE_ID_reconcile_scan`.
  - `reconcile_bp_del()` validates and deletes a reconcile scan backpointer.
  - `reconcile_bp_get_key()` resolves a reconcile backpointer to a btree node key and repairs stale/missing records.
- `__bch2_trigger_extent_reconcile()` is the core trigger. Transactionally, it moves leaf keys between normal/hipri/pending work bit btrees or manages btree-node reconcile backpointers. In transactional/GC modes it also updates reconcile accounting and dev-leaving counters for moving pointers.
- `bch2_bkey_needs_reconcile()` computes desired reconcile state from current IO opts, key pointers, CRC/compression, targets, device evacuation, durability, EC, invalid placeholder pointers, unwritten/incompressible/poisoned state, and old pending/hipri state.
- `new_needs_rb_allowed()` fsck-validates new reconcile requirements, allowing known exceptions for option-change scans, foreground writes, missing initial EC on foreground writes, option-change races, indirect extents, and scan cookies.
- `bch2_bkey_set_needs_reconcile()` mutates a mutable key: add/update/drop reconcile entries, set stripe `needs_reconcile`, add or remove `BCH_SB_MEMBER_INVALID` placeholder pointers, and update `trans->extra_disk_res` when placeholders add durability obligations.
- `bch2_extent_trigger_set_needs_reconcile()` grows trigger-owned new keys when needed and fills reconcile metadata lazily from IO opts.
- `bch2_update_reconcile_opts()` updates leaf keys or btree node keys already in a scan/check path, using transaction kmalloc and btree node update for interior levels.
- `bch2_bkey_get_io_opts()` derives effective IO options for metadata, reflink/indirect, and user data. With `per_snapshot_io_opts`, it caches inode options by inode and snapshot ancestry during ordered scans. For reflink values, persisted reconcile options can override inode-derived fields and are re-run through IO option fixups.

## Dependencies and Coupling
Depends on extent entry iteration, disk accounting, btree bit updates, btree node update, inode option lookup, snapshot ancestry, reconcile scan cookies, compression/checksum option helpers, and fsck error reporting.

## Risks and Invariants
- New reconcile requirements are tightly controlled; unexpected missing/incorrect reconcile opts are treated as fsck errors unless a scan cookie or recognized race explains them.
- Multiple `BCH_SB_MEMBER_INVALID` placeholder pointers may require a reconcile incompat feature; otherwise the function clamps updates.
- Trigger behavior differs for leaf data and interior btree nodes; btree nodes need explicit reconcile scan backpointers because they cannot be tracked in the same leaf work bitsets.
