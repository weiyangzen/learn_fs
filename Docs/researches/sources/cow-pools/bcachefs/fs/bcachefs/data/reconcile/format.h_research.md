# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/format.h

## Role

`reconcile/format.h` defines on-disk metadata used to track background data reconciliation: replica correction, checksum changes, compression changes, target movement, EC changes, high-priority evacuation, pending work, and btree-node backpointers.

## Main Structures

- `struct bch_extent_rebalance_v1`: older on-disk rebalance options entry.
- `struct bch_extent_reconcile`: current reconcile entry embedded in extent-entry streams.
- `struct bch_extent_reconcile_bp`: index of a reconcile scan backpointer for btree-node keys.

## Reconcile Options

`BCH_RECONCILE_OPTS()` covers:
- data replicas
- data checksum
- erasure code
- background compression
- background target
- promote target

Each option can store both a value and whether it came from inode options.

## Work Btrees

The comments define the reconcile work model:
- `BTREE_ID_reconcile_scan`: scan cookies and btree-node backpointers.
- `BTREE_ID_reconcile_work`: normal pending extent work.
- `BTREE_ID_reconcile_hipri`: high-priority pending work, especially failed-device evacuation.
- `BTREE_ID_reconcile_pending`: work blocked because a desired target is unavailable/full.

Physical variants are mapped by `reconcile_work_phys_btree[]`.

## Accounting Types

`BCH_RECONCILE_ACCOUNTING()` defines counters for replica, checksum, EC, compression, target, high priority, pending, and stripes work.

## Scan Cookies

Cookie IDs distinguish filesystem-wide scans, metadata scans, pending scans, stripe scans, and per-device scans.
