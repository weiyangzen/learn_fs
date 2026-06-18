# sources/distributed-fs/ceph-client/fs/xfs/scrub/rmap.c

## Purpose
`rmap.c` scrubs the per-AG reverse mapping btree. It validates rmap records, detects illegal overlaps and mergeable adjacent records, cross-references mapped space with allocation, inode, and refcount metadata, and compares AG metadata rmaps against independently collected metadata block bitmaps.

## Important APIs, types, and functions
`xchk_setup_ag_rmapbt` prepares AG rmap scrub and optional repair. `struct xchk_rmap` tracks previous/overlap records and bitmaps for `OWN_FS`, `OWN_LOG`, `OWN_AG`, `OWN_INOBT`, and `OWN_REFC`. Important helpers are `xchk_rmapbt_xref_refc`, `xchk_rmapbt_check_unwritten_in_keyflags`, `xchk_rmapbt_check_overlapping`, `xchk_rmapbt_check_mergeable`, `xchk_rmapbt_walk_ag_metadata`, `xchk_rmapbt_mark_bitmap`, `xchk_rmapbt_check_bitmaps`, and `xchk_rmapbt`. Exported xref helpers include `xchk_xref_is_only_owned_by`, `xchk_xref_is_not_owned_by`, and `xchk_xref_has_no_owner`.

## Control flow
Scrub builds expected AG metadata bitmaps by walking AG headers, log placement, bnobt/cntbt/rmapbt/AGFL, inode btrees, finobt, and refcountbt. It then walks the rmapbt. Each record is decoded and checked, btree node key flags are inspected for stale unwritten bits, mergeability and overlap rules are applied, cross-reference checks are run, and matching metadata bitmap ranges are cleared. After the walk, remaining set bits indicate missing rmap coverage.

## State and persistence
The file is read-only from a filesystem perspective. It records scrub flags and uses temporary `xagb_bitmap` state. Preen is used for historical unwritten bits in internal rmap keys; corrupt and xcorrupt flags distinguish primary failures from cross-reference mismatches.

## Dependencies and integration points
It depends on allocation, inode, refcount, rmap btree APIs, AGFL walking, scrub bitmap helpers, and repair setup. Many other scrubbers rely on its xref helpers to validate ownership constraints.

## Risks and test signals
Risks include false xref corruption from incomplete metadata bitmap walks, shareability filtering mistakes for reflink data, stale key flag handling, AGFL stale block confusion, and owner/unit mismatches. Tests should cover overlapping metadata rmaps, overlapping shared data, adjacent mergeable records, internal log AGs, sparse inode btrees, finobt/refcountbt optional features, stale unwritten key flags, and missing or extra AG metadata rmaps.
