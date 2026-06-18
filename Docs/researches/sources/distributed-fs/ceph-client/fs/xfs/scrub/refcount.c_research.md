# sources/distributed-fs/ceph-client/fs/xfs/scrub/refcount.c

## Purpose
`refcount.c` scrubs the per-AG XFS reference count btree. It validates refcount records for shared extents and CoW staging extents, checks ordering and mergeability, cross-references refcount ownership against allocation/inode/rmap metadata, and exports helper xref checks for other scrubbers.

## Important APIs, types, and functions
The setup entry point is `xchk_setup_ag_refcountbt`, which enables intent draining when needed, runs `xrep_setup_ag_refcountbt` if repair is possible, and then uses generic AG btree setup. The main scrub entry is `xchk_refcountbt`. `struct xchk_refcnt_check` and `struct xchk_refcnt_frag` track rmap coverage while verifying a single refcount record. `struct xchk_refcbt_records` tracks previous records, shared-gap boundaries, CoW block totals, and domain ordering. Public xref helpers include `xchk_xref_is_cow_staging`, `xchk_xref_is_not_shared`, and `xchk_xref_is_not_cow_staging`.

## Control flow
`xchk_refcountbt` walks `sc->sa.refc_cur` with `xchk_btree` and `xchk_refcountbt_rec`. Each record is decoded, checked with `xfs_refcount_check_irec`, counted if CoW, checked for shared-before-CoW ordering, checked for adjacent mergeable records, and cross-referenced. Rmap verification queries overlapping rmap records, counts full-span owners immediately, saves partial fragments, and then simulates fragment coverage to prove every block reaches the advertised refcount. Shared-record gaps are queried against rmapbt to detect unrecorded overlap. After the walk, tail gaps and refcountbt/CoW block counts are checked against rmap ownership totals.

## State and persistence
The file does not persist new state. It consumes on-disk refcount/rmap/allocation/inode btrees through scrub cursors and records corruption, xref corruption, or preen bits in `sc->sm->sm_flags`. Temporary rmap fragments are heap allocated and freed during each record check.

## Dependencies and integration points
It depends on libxfs refcount and rmap btree APIs, scrub btree walkers, AG scrub setup, and repair setup from `repair.h`. Other scrubbers call its xref helpers to reject shared or CoW-staging blocks where inappropriate.

## Risks and test signals
Risk centers on fragment accounting, domain ordering, CoW single-owner semantics, and distinguishing xref failures from refcountbt corruption. Tests should cover fragmented shared extents, adjacent mergeable records, shared gaps, CoW records with non-CoW rmaps, missing rmap owners, rmapbt count mismatches, no-rmap/reflink-disabled configurations, and termination during fragment allocation.
