# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrmap.c

## Purpose
`rtrmap.c` scrubs the realtime reverse mapping btree for an rtgroup. It validates rtrmap records, checks illegal overlaps and mergeable adjacent records, verifies the rtrmap metadata inode, and cross-references realtime ownership against rtbitmap and rtrefcount metadata.

## Important APIs, types, and functions
`xchk_setup_rtrmapbt` prepares rtgroup state, optional repair, live rtrmap inode, and rtgroup locks. `struct xchk_rtrmap` tracks the furthest overlapping record and previous record. Main helpers are `xchk_rtrmapbt_check_overlapping`, `xchk_rtrmap_mergeable`, `xchk_rtrmapbt_check_mergeable`, `xchk_rtrmapbt_xref_rtrefc`, `xchk_rtrmapbt_xref`, `xchk_rtrmapbt_rec`, and `xchk_rtrmapbt`. Exported xref helpers are `xchk_xref_has_no_rt_owner`, `xchk_xref_has_rt_owner`, and `xchk_xref_is_only_rt_owned_by`.

## Control flow
After setup and metadata inode fork scrub, `xchk_btree` walks `sc->sr.rmap_cur`. Each record is decoded and checked with `xfs_rtrmap_check_irec`. If still clean, it checks whether adjacent records should have merged, whether overlaps are legal shareable realtime data mappings, and whether the range is used in the rtbitmap. CoW records are checked against CoW staging metadata, and non-CoW records are checked against rtrefcount to ensure shared extents describe valid written data owners.

## State and persistence
Scrub is read-only and records flags in scrub metadata. The local `xchk_rtrmap` context stores only previous/overlap records for one btree walk.

## Dependencies and integration points
It depends on rtgroup locks, rtrmap btree APIs, metadata inode fork scrub, rtbitmap used-space xref, rtrefcount xref, and repair setup. Other realtime scrubbers use its exported xref helpers to prove presence or absence of realtime owners.

## Risks and test signals
Risks include permissive overlap checks, incorrect shareability when rtreflink is disabled, use of AG refcount helper names in CoW xref paths, and owner-count false positives. Tests should include overlapping metadata records, overlapping shared realtime file records, unwritten shared extents, adjacent mergeable records, free-space rmaps, shared extents without rtrefcount records, CoW staging mismatches, and missing metadata inode blocks.
