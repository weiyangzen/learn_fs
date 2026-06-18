# File Research: sources/cow-pools/bcachefs-tools/fs/data/reflink.c

## Role

Implements bcachefs reflink and indirect extent mechanics. It validates and prints reflink keys, follows reflink pointers into the reflink btree, maintains indirect refcounts through triggers, converts extents to indirect extents, remaps source ranges into destination files, and repairs/refcounts indirect extents during GC/fsck.

## Key Types Handled

- `KEY_TYPE_reflink_p`: pointer stored in the extents btree, containing an indirect index plus front/back pad and flags.
- `KEY_TYPE_reflink_v`: indirect extent stored in the reflink btree, containing refcount plus normal extent entries.
- `KEY_TYPE_indirect_inline_data`: indirect refcounted inline data.

## Validation and Printing

`bch2_reflink_p_validate()` checks that `REFLINK_P_IDX` is not before `front_pad`. `bch2_reflink_v_validate()` rejects indirect extent positions above `REFLINK_P_IDX_MAX` and delegates pointer validation to `bch2_bkey_ptrs_validate()`. Inline indirect data validation is currently a no-op.

Text printers show pointer index, pads, `error`, `may_update_opts`, indirect refcounts, extent pointers, and inline data bytes.

## Lookup and Missing-Extent Repair

`bch2_lookup_indirect_extent()` maps a reflink pointer plus offset to the corresponding key in `BTREE_ID_reflink`. If the target data is missing, `bch2_indirect_extent_missing_error()` reports an fsck error and either adjusts pads for gaps outside the live range or cuts/marks the pointer with `REFLINK_P_ERROR` for live missing data. If a previously errored pointer now resolves correctly, `bch2_indirect_extent_not_missing()` clears the error flag.

The lookup is used both by the read path and by triggers, so it accepts a `should_commit` flag to control whether it may commit repairs directly.

## Refcount Triggers

`bch2_trigger_reflink_p()` resets pads for newly inserted pointers, then runs overwrite-before-insert trigger logic. Transactional trigger handling walks every indirect segment covered by the pointer including pads, increments refcounts on insert, decrements on overwrite/delete, and expands pointer pads when the indirect extent is larger than the nominal reference.

GC trigger handling uses `c->reflink_gc_table`, a sorted genradix table of indirect extents prepared by `bch2_gc_reflink_start()`, to accumulate expected refcounts. `bch2_reflink_p_check_repair()` uses the same machinery with repair enabled.

`bch2_trigger_reflink_v()` and `bch2_trigger_indirect_inline_data()` delete indirect keys when their refcount reaches zero. `reflink_v` then delegates to the normal extent trigger so underlying pointer accounting is updated.

## Making Extents Indirect

`bch2_make_extent_indirect()` converts a direct extent or inline data extent into an indirect extent:

- Ensures the relevant reflink feature bit is set.
- Captures inode IO options into the new indirect extent's reconcile entry so a reflinked extent does not later reconcile against filesystem defaults.
- Allocates the new key at the end of `BTREE_ID_reflink`, subject to the 56-bit `REFLINK_P_IDX_MAX` limit.
- Copies the original value after a zero refcount.
- Inserts the indirect key, then mutates the original key into a `reflink_p` pointing at it.
- Optionally sets `REFLINK_P_MAY_UPDATE_OPTIONS`.

## Range Remapping

`bch2_remap_range()` is the reflink clone/remap operation. It obtains a write reference, sets the reflink feature, resolves source and destination snapshots, walks source data extents, punches destination holes for source gaps, converts direct source extents to indirect extents as needed, creates destination `reflink_p` keys, and inserts them through `bch2_extent_update()`.

After the remap loop it updates the destination inode size when necessary. It returns the number of destination sectors completed, or an error if no progress was made.

## GC/FSCK Refcount Repair

`bch2_gc_reflink_start()` walks `BTREE_ID_reflink` and builds a genradix table containing every refcounted indirect extent with zero observed references. Reflink pointer GC triggers add/subtract to those observed counts. `bch2_gc_reflink_done()` walks the reflink btree again, compares stored refcounts to observed counts, fixes mismatches, and deletes indirect keys whose observed refcount is zero.
