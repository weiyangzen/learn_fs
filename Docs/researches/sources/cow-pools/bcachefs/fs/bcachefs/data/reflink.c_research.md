# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink.c

Implements reflink pointer validation/text, indirect extent lookup, refcount triggers, reflink creation/remap, and reflink fsck/GC refcount repair.

Key entry points:
- `bch2_reflink_p_validate()`, `bch2_reflink_p_to_text()`, `bch2_reflink_p_merge()` implement bkey operations for `KEY_TYPE_reflink_p`; merging is currently disabled.
- `bch2_reflink_v_validate()` and `bch2_reflink_v_to_text()` handle indirect extent values in the reflink btree.
- `bch2_indirect_inline_data_validate()` and `bch2_indirect_inline_data_to_text()` support reflinked inline data.
- `bch2_lookup_indirect_extent()` follows a reflink pointer into `BTREE_ID_reflink`, repairs missing-range state when requested, and returns the indirect data key plus offset.
- `bch2_trigger_reflink_p()`, `bch2_trigger_reflink_v()`, and `bch2_trigger_indirect_inline_data()` maintain refcounts and delete zero-ref indirect extents.
- `bch2_remap_range()` implements clone/remap by converting source data to indirect extents and inserting destination reflink pointers.
- `bch2_gc_reflink_start()` and `bch2_gc_reflink_done()` build/check the GC refcount table and repair wrong refcounts.

Important invariants:
- `REFLINK_P_IDX` must not be smaller than `front_pad`; indirect values must not exceed `REFLINK_P_IDX_MAX`.
- Reflink pointer triggers walk the full referenced range, including `front_pad` and `back_pad`, so split indirect extents do not leak refcounts.
- Missing indirect data in the live range sets `REFLINK_P_ERROR`; missing ranges only in padded regions shrink pads instead.
- Indirect extents with refcount zero are transformed to deleted keys before normal extent triggers run.
- Source extent conversion snapshots IO options into the new indirect extent’s reconcile entry so background reconcile does not use filesystem defaults for shared data.
- `bch2_remap_range()` uses write refs, snapshot lookup, extent punching for holes, and regular extent update to maintain destination inode size/sector accounting.

Dependencies and interactions:
- Uses btree transactions, extent helpers, reconcile trigger helpers, write extent update, inode/subvolume lookup, fsck error reporting, enumerated write refs, and the reflink GC genradix table.
