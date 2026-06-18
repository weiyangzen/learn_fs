# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrefcount.c

## Purpose
`rtrefcount.c` scrubs the realtime refcount btree for an rtgroup. It mirrors AG refcount scrub logic but uses rtgroup-local block units, checks realtime extent alignment, validates the metadata inode, and cross-references records against realtime bitmap, realtime rmap, and data-device rmaps for the rtrefcount btree inode.

## Important APIs, types, and functions
`xchk_setup_rtrefcountbt` initializes rtgroup state, optional repair setup, live rtrefcount inode, and all rtgroup locks. `xchk_rtrefcountbt` is the main scrubber. `struct xchk_rtrefcnt_check` and `xchk_rtrefcnt_frag` implement rmap fragment counting. `struct xchk_rtrefcbt_records` tracks previous records, unshared gaps, CoW block totals, and domain order. Xref helpers are `xchk_xref_is_rt_cow_staging`, `xchk_xref_is_not_rt_shared`, and `xchk_xref_is_not_rt_cow_staging`.

## Control flow
After metadata inode fork scrub, `xchk_btree` walks `sc->sr.refc_cur`. Each record is decoded, checked with `xfs_rtrefcount_check_irec`, verified to start and end on realtime extent boundaries, checked for shared-before-CoW ordering and mergeability, and cross-referenced. Rmap xref counts complete and fragmentary rtrmap records to prove the advertised refcount. Shared-record gaps are queried for unexpected overlaps. Final checks compare rtrefcount btree block counts against data-device rmap ownership for the metadata inode and CoW blocks against realtime rmap ownership.

## State and persistence
The file is read-only and sets scrub flags. Temporary fragment lists are allocated per record. It uses `sc->sr` realtime cursors and `sc->sa.rmap_cur` when counting data-device blocks belonging to the rtrefcount metadata btree inode.

## Dependencies and integration points
It depends on rtgroup locking, rtrefcount/rtrmap btree APIs, realtime bitmap xref, metadata inode fork scrub, and repair setup. Realtime rmap and bitmap scrubbers call its xref helpers to reject shared or CoW-staging ranges.

## Risks and test signals
Risks include unit conversion errors, full-rt-extent alignment checks, fragment coverage mistakes, and mismatched data-device rmap counts for metadir btree blocks. Tests should cover aligned and misaligned records, fragmented shared realtime extents, CoW records, shared gaps, missing rtrmap owners, wrong metadata inode rmaps, no-rtreflink paths, and xref skip/failure behavior.
