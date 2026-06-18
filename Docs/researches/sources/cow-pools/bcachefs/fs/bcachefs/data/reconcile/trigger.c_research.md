# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/trigger.c

## Role

`reconcile/trigger.c` translates extent state and I/O policy into reconcile metadata, work queues, backpointers, and accounting. It is called from btree triggers, fsck/update scans, foreground writes, option-change propagation, and movement paths.

## Validation and Formatting

- `bch2_extent_reconcile_validate()` rejects bad pending, hipri, or replica fields.
- `bch2_extent_rebalance_v1_to_text()` and `bch2_extent_reconcile_to_text()` print old and new reconcile entries.
- `bch2_bkey_reconcile_opts()` finds the reconcile entry in a key’s extent-entry stream.
- `bch2_bkey_reconcile_work_id()` returns none/hipri/normal/pending for a key.

## Reconcile Backpointers

Btree pointer keys need reconcile scan backpointers because normal leaf work bit btrees track extents/reflink/stripes, not btree nodes.

Functions:
- `bch2_bkey_get_reconcile_bp_pos()`
- `bch2_bkey_set_reconcile_bp()`
- `reconcile_bp_add()`
- `reconcile_bp_del()`
- `reconcile_bp_get_key()`

These maintain `BTREE_ID_reconcile_scan` entries that point back to btree node keys.

## Trigger Effects

`__bch2_trigger_extent_reconcile()` handles two classes of side effects:
- Transactional work index updates: moving logical keys between normal/hipri/pending bit btrees, or adding/removing btree-node reconcile backpointers.
- Transactional/GC accounting: updating `reconcile_work` counters and device-leaving counters based on old/new reconcile entries and key sizes.

`bch2_trigger_extent_reconcile()` skips the full trigger when neither old nor new reconcile metadata needs work or device accounting.

## Determining Need for Reconcile

`bch2_bkey_needs_reconcile()` compares actual key pointers and encoded formats against target I/O options:
- checksum type,
- compression type,
- background target,
- data replicas/durability,
- erasure-code state,
- evacuating/bad devices,
- invalid-device placeholders,
- poisoned/unwritten/incompressible constraints.

It sets:
- `need_rb` option bits,
- `hipri` for degraded/evacuating cases,
- `ptrs_moving` for pointers moving off devices/targets,
- `pending` preservation where applicable,
- invalid-device placeholder add/drop count.

## Writing Reconcile Entries

`bch2_bkey_set_needs_reconcile()` mutates a key to add, update, or drop `bch_extent_reconcile`, and may add/drop `BCH_SB_MEMBER_INVALID` placeholder pointers for durability accounting.

`bch2_extent_trigger_set_needs_reconcile()` grows trigger-mutated keys as needed and fills reconcile metadata automatically.

`bch2_update_reconcile_opts()` is the scanner/update path; for leaf keys it creates a mutable copy and updates it, while for btree-node keys it updates the node key through btree-node update infrastructure.

## Option Lookup

`bch2_bkey_get_io_opts()` computes applicable I/O options for metadata, user extents, and reflink data:
- metadata uses filesystem metadata options,
- user data can use per-inode snapshot-specific options,
- reflink values can preserve inode-derived options stored in reconcile metadata.

`per_snapshot_io_opts` caches inode options while scanning natural key order.

## Safety Checks

`new_needs_rb_allowed()` prevents unexpected new reconcile needs unless they are justified by option-change scans, foreground-write allowances, EC creation timing, device scan cookies, or cached scan-cookie state. Otherwise fsck reports incorrect/missing reconcile options.

## Invariants

- Pending reconcile requires `need_rb`.
- Hipri reconcile is tied to replica/durability work.
- Reconcile entries are omitted when not needed, except reflink values may retain inode-derived options.
- Btree pointer reconcile backpointers are transactional and must move when work id changes.
- Pending work suppresses target/replica accounting in favor of pending accounting.
