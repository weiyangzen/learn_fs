# sources/distributed-fs/ceph-client/fs/xfs/scrub/alloc.c

## Purpose
This file scrubs the XFS free-space btrees: bnobt ordered by block number and cntbt ordered by length. It validates individual free-space records, checks that matching records exist in the sibling free-space tree, detects mergeable adjacent records, and exposes a shared xref helper to verify that a block range is not free.

## Important APIs, types, and functions
`xchk_setup_ag_allocbt` prepares AG btree scrub, enables intent draining if needed, and invokes `xrep_setup_ag_allocbt` when repair might run. `xchk_allocbt` selects `sc->sa.bno_cur` or `sc->sa.cnt_cur` based on scrub type and runs `xchk_btree`. `xchk_allocbt_rec` decodes `xfs_alloc_rec_incore` records and validates them with `xfs_alloc_check_irec`. `xchk_allocbt_xref_other` confirms the corresponding record exists in the other free-space btree. `xchk_allocbt_mergeable` preens corruption when adjacent records could be coalesced. `xchk_xref_is_used_space` is a reusable xref helper used by many scrubbers.

## Control flow and state
Setup locks the AG btree context. Record scrub decodes each btree record, validates extent bounds, checks local ordering through `struct xchk_alloc.prev`, cross-references the peer tree, ensures the free space is not an inode chunk, has no rmap owner, is not shared, and is not CoW staging. The scrub stops marking deeper xref findings once global corruption is already present.

## Persistence and integration
The file does not mutate filesystem metadata. It depends on AG btree cursors, inode allocation xrefs, rmap ownership checks, refcount checks, and common btree scrub machinery. Its `xchk_xref_is_used_space` helper is central to header, bmap, and metadata scrubbers that need to prove their blocks are allocated.

## Risks and test signals
Risks include incorrect peer-tree matching between differently ordered trees, failing to flag mergeable free records, and suppressing xrefs too aggressively when one cursor fails. Tests should cover malformed alloc records, adjacent free extents that should merge, bnobt/cntbt mismatches, free extents overlapping inode chunks or shared/COW space, and `xchk_xref_is_used_space` behavior for empty, full, and partially overlapping record packing outcomes.
