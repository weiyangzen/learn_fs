# sources/distributed-fs/ceph-client/fs/xfs/scrub/bmap.c

## Purpose
This file scrubs inode block mappings for data, attribute, and CoW forks. It validates fork formats, bmap btree records, in-core extent cache records, delalloc reservations, and cross-references mappings against allocation, inode, reverse mapping, refcount, CoW staging, and realtime metadata.

## Important APIs, types, and functions
`xchk_setup_inode_bmap` obtains and locks the inode, flushes regular file state, waits for direct I/O, optionally invalidates page cache for repair, allocates a transaction, attaches quotas, and takes ILOCK. `struct xchk_bmap_info` tracks scrub context, cursor, previous record, fork, realtime/shared flags, and whether extents were loaded. `xchk_bmap` is the shared scrub driver; `xchk_bmap_data`, `xchk_bmap_attr`, and `xchk_bmap_cow` are public entry points. Helpers include `xchk_bmap_btree`, `xchk_bmapbt_rec`, `xchk_bmap_iext_iter`, datadev/realtime xref functions, rmap exact-match checks, and empty-fork rmap scans.

## Control flow and state
Setup stabilizes ephemeral writes before inspecting mappings. The scrub driver rejects impossible fork formats, scans the bmbt if the fork is in btree format, then iterates the in-core extent list. The iterator merges logically and physically contiguous mappings to reduce xref work and preens files that could use fewer bmbt records. Real extents are validated for file range, physical range, unwritten rules, directory/attr dablock addressability, and then cross-referenced. Delalloc extents are validated only for logical range and maximum bmbt length. If a fork appears zapped, optional rmap scans verify whether rmaps still exist for the inode.

## Persistence and integration
This file is read-only validation, but it flushes data and can invalidate page cache before repair. It integrates with AG and realtime group scrub state, rmap/refcount btrees, health flags for zapped forks, quota setup, inode locks, and btree scrub. It understands reflink sharing and COW staging ownership distinctions.

## Risks and test signals
Risks include stale in-core extent cache versus disk btree, delalloc handling, realtime group boundaries, reflink rmap lookup semantics, and empty-fork recovery heuristics. Tests should cover btree owner mismatches, bmbt/incore divergence, contiguous merge preen, attr fork unwritten extents, COW fork on non-reflink filesystems, zapped data/attr forks with rmap residue, realtime rmap/refcount xrefs, shared data fork extents, and writeback errors during setup.
