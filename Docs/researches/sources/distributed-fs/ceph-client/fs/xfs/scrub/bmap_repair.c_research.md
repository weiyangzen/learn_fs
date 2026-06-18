# sources/distributed-fs/ceph-client/fs/xfs/scrub/bmap_repair.c

## Purpose
This file repairs an inode data or attr fork block map by reconstructing mappings from reverse mapping records. It builds a new in-core extent tree and, when needed, a new bmap btree; updates inode block counts, quota counts, and reflink flags; and reaps blocks from the old bmbt.

## Important APIs, types, and functions
`struct xrep_bmap` stores old bmbt block bitmap, newbt state, collected bmap records, block counters, fork selection, reflink scan state, and unwritten-extent policy. `xrep_bmap` is the shared repair entry point, with `xrep_bmap_data` and `xrep_bmap_attr` wrappers. Collection helpers include `xrep_bmap_scan_ag`, `xrep_bmap_scan_rtgroup`, `xrep_bmap_walk_rmap`, `xrep_bmap_walk_rtrmap`, and `xrep_bmap_find_delalloc`. Build helpers include `xrep_bmap_sort_records`, `xrep_bmap_extents_load`, `xrep_bmap_btree_load`, `xrep_bmap_build_new_fork`, and `xrep_bmap_remove_old_tree`.

## Control flow and state
Input checks require rmapbt and accept only extents or btree fork formats. Repair allocates an `xfarray` sized to the maximum fork extent count, scans realtime rmaps and per-AG rmaps, validates every candidate rmap against allocation and inode metadata, records all blocks for `i_nblocks`, records old bmbt blocks, and converts fork rmaps into bmbt records split at `XFS_MAX_BMBT_EXTLEN`. Delalloc reservations from the old in-core tree are preserved. Records are sorted by logical offset and checked for overlap. The new fork is staged as extents if it fits or as a bulk-loaded btree otherwise, then committed into the inode.

## Persistence and integration
The repair joins the inode to the transaction, reserves blocks for a new btree as needed, commits staged btree/fork roots, logs inode core changes, updates quota block counts by the bmbt-size delta, commits newbt reservations, rolls transactions, and reaps old bmbt blocks using the correct owner info. Reflink state is recalculated by consulting refcount records for discovered shared extents.

## Risks and test signals
Risks include trusting damaged rmap records, reconstructing realtime and datadev mappings together, preserving delalloc correctly, setting `XFS_DIFLAG2_REFLINK` only when warranted, and keeping `i_nblocks`/quota accurate after btree size changes. Tests should include zapped forks rebuilt from rmap, attr fork rejecting unwritten extents, realtime data mappings, old bmbt block reaping, large extent counts, split records above max bmbt length, overlap detection after sort, non-file data fork rejection, shared extent reflink flag discovery, and failure cleanup for newbt reservations.
