# sources/distributed-fs/ceph-client/fs/xfs/scrub/agheader_repair.c

## Purpose
This file repairs AG header structures: secondary superblocks, AGF, AGFL, and AGI. The design uses reliable metadata such as the primary superblock, rmapbt records, live btrees, incore inode state, and temporary bitmaps/arrays to reconstruct damaged headers, commit them transactionally, and refresh per-AG in-core counters.

## Important APIs, types, and functions
`xrep_superblock` rewrites a secondary superblock from `mp->m_sb`, clearing secondary-ignored NEEDSREPAIR and log incompat flags. `xrep_agf` reconstructs AGF roots and counters using `xrep_find_ag_btree_roots`, `xrep_agf_set_roots`, and `xrep_agf_calc_from_btrees`. `xrep_agfl` rebuilds the AGFL from OWN_AG rmap records after subtracting actual btree metadata and crosslinked blocks. `xrep_agi` rebuilds AGI btree roots, inode counters, and iunlink lists. `struct xrep_agi` stores AGI repair context, old header backup, staged iunlink heads, `xagino_bitmap`, and `xfarray` maps for next/prev iunlink pointers. `struct xrep_agfl` and `struct xrep_agfl_fill` manage AGFL block collection and formatting.

## Control flow and state
AGF repair requires rmapbt support. It reads the raw AGF, reads and sanity-checks AGFL, finds btree roots, takes a final termination checkpoint, rewrites the AGF header, implants roots, recalculates counters from btrees, logs the buffer, updates `pagf_*`, sets `XFS_AGSTATE_AGF_INIT`, and rolls the AG transaction. AGFL repair derives candidate blocks from OWN_AG mappings, removes currently used btree blocks and crosslinked blocks, writes a new AGFL, updates AGF flcount/first/last, rolls the transaction, and reaps overflow blocks. AGI repair finds inobt/finobt roots, reconstructs iunlink state from ondisk buckets, incore inode cache, and ondisk inode scans, then rewrites header fields, counters, and unlinked bucket heads.

## Persistence and integration
All repairs are transactional and use buffer type tagging plus `xfs_trans_log_buf` or inode logging helpers. Perag initialization bits are cleared while headers are unsafe and set after reinitialization. Summary counters are forced to recalc after AGF/AGI changes. AGFL overflow and stale metadata are returned through reap helpers, which depend on accurate rmap ownership.

## Risks and test signals
The principal risk is chicken-and-egg reconstruction: AGF and AGFL both depend on rmapbt and AGFL data even when headers are damaged. AGI iunlink repair is sensitive to races, cached inode lifetime, and correct forward/back pointer logging. Tests should cover missing rmapbt rejection, bad AGFL candidates, refcount feature root handling, AGF counter recomputation, iunlink cycles or wrong buckets, uncached unlinked inodes, transaction roll failures, and rollback paths that restore old headers after calculation errors.
