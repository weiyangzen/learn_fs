<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters_repair.c

Purpose: Repairs filesystem summary counters by resetting the in-core counters to the values computed during the mandatory scrub phase.

Important APIs, types, and functions: Exports `xrep_fscounters()`, which consumes `struct xchk_fscounters` from `sc->buf` and updates `m_icount`, `m_ifree`, `XC_FREE_BLOCKS`, `XC_FREE_RTEXTENTS`, and sometimes `sb_frextents`.

Control flow: Repair first asserts that the filesystem was frozen during scrub and refuses to proceed otherwise. It then sets inode and free-block percpu counters to scrubbed values. Realtime free extents are adjusted by subtracting delayed realtime reservations for the in-core freecounter; on non-rtgroup realtime filesystems it also updates `mp->m_sb.sb_frextents`.

State and persistence: The direct writes are to in-memory counters and the mounted superblock copy. Online repair relies on v5 lazy superblock counters for data block persistence, while realtime free extent handling still needs explicit superblock-state correction on configurations without rtgroups.

Dependencies and integration points: Depends on `fscounters.c` for accurate computed values and freeze ownership, on XFS freecounter helpers, realtime/zoned feature predicates, and scrub tracepoints. It is invoked by the scrub/repair framework only after a corrupt counter finding.

Risks and test signals: The high-risk path is repairing from unfrozen or incomplete observations; the code guards this with `frozen`. Test repair after clean frozen aggregation, refusal without freeze, realtime with delayed allocations, zoned filesystems skipping frextents, rtgroup vs non-rtgroup superblock updates, and post-repair rescrub equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters_repair.c -->
