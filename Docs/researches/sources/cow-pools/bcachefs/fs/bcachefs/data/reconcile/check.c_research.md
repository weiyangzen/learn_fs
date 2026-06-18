# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/check.c

## Role

`reconcile/check.c` verifies and repairs reconcile work indexes. It ensures that logical data keys, physical backpointers, btree-node reconcile backpointers, and stripe widening metadata agree with the current reconcile state.

## Logical Work Check

`check_reconcile_work_one()` compares:
- the data key’s computed reconcile work id,
- `BTREE_ID_reconcile_work`,
- `BTREE_ID_reconcile_hipri`,
- `BTREE_ID_reconcile_pending`.

If bits are set in the wrong work btree, fsck can call `fix_reconcile_work_btree()` to update buffered bit btrees.

It also calls `bch2_bkey_get_io_opts()` and `bch2_update_reconcile_opts()` to refresh reconcile opts on the data key.

`check_reconcile_work_data_btree()` runs this over stripes, reflink, and extents btrees.

## Physical Work Check

`check_reconcile_work_phys_one()` compares backpointer `BACKPOINTER_RECONCILE_PHYS()` state against physical work bit btrees:
- `BTREE_ID_reconcile_work_phys`
- `BTREE_ID_reconcile_hipri_phys`

It repairs incorrect physical bits through the same buffered bit modification helper.

## Btree Pointer Reconcile Backpointers

`check_reconcile_work_btree_key()` validates that btree pointer keys that need reconcile have a valid `reconcile_bp` entry and that the target `BTREE_ID_reconcile_scan` backpointer points back to the correct btree node key.

It repairs:
- missing reconcile backpointer entries,
- bad reconcile backpointer entries,
- missing scan backpointer records,
- conflicting scan positions by allocating a new empty slot.

## Stripe Widening Check

`check_stripe_can_widen()` verifies each stripe’s stored `can_widen` value against the current disk-label RW member count and EC max data block policy. If a stripes scan cookie is pending, drift is expected and not flagged.

## Entry Point

`bch2_check_reconcile_work()` runs:
1. logical data-btree work check,
2. physical backpointer work check,
3. btree pointer reconcile backpointer check,
4. reconcile scan backpointer validation,
5. stripe `can_widen` validation.

## Invariants

- Work bits must exist in exactly one reconcile work btree or none.
- Logical work positions map extents/reflink/stripes into a shared position namespace.
- Physical pending work is derived from backpointer metadata.
- Btree nodes use reconcile scan backpointers because regular work btrees cannot track them directly.
