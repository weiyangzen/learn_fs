# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap.c

## Purpose
`rtbitmap.c` scrubs the realtime bitmap metadata for an rtgroup. It verifies realtime geometry fields, metadata inode shape, mapped/written bitmap file extents, free extent records returned by rt allocation queries, and cross-references free/used realtime space against rtrmap and rtrefcount metadata.

## Important APIs, types, and functions
`xchk_setup_rtbitmap` allocates `struct xchk_rtbitmap`, initializes the rtgroup, optional repair setup, transaction reservation, live bitmap inode, dquots, and rtgroup locks. `xchk_rtbitmap` is the main scrubber. Helpers include `xchk_rtbitmap_xref`, `xchk_rtbitmap_rec`, `xchk_rtbitmap_check_extents`, and exported `xchk_xref_is_used_rt_space`.

## Control flow
Setup computes expected `rextents`, `rextslog`, and `rbmblocks` after locking the rtgroup to avoid growfs races. Scrub compares superblock geometry against computed values, checks bitmap file size/alignment, delegates inode/fork scrutiny to metadata inode scrub, and ensures the file has only written mappings. It then walks all free realtime extents with `xfs_rtalloc_query_all`. Each record is verified, cross-referenced as having no rtrmap owner and no shared/CoW refcount records, and gaps between free records are checked as owned. The tail of the group is checked similarly.

## State and persistence
Scrub is read-only and updates only scrub flags plus `next_free_rgbno` in the transient `xchk_rtbitmap`. No bitmap changes are written here; repair lives in `rtbitmap_repair.c`.

## Dependencies and integration points
It depends on rtgroup locking, rt allocation query APIs, metadata inode fork scrub, bmap read APIs, rtrmap xref helpers, rtrefcount helpers, zone validation for zoned filesystems, and repair setup through `rtbitmap.h`.

## Risks and test signals
Risks include off-by-one tail checks, extent/rtblock/rtgroup-block conversion mistakes, growfs races, zoned filesystem special cases, and inability to xref when rtrmap is unavailable. Tests should cover zero-sized rt volumes, oversized `rbmblocks`, unwritten or hole bitmap mappings, malformed free extents, free extents with rmap owners, used gaps without owners, rtreflink CoW/shared conflicts, and zoned rtgroup bounds.
