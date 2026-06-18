<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc.c

Purpose: Scrubs the inode allocation btrees, validating inobt and finobt records against inode cluster buffers, each other, free-space ownership, and reverse mappings.

Important APIs, types, and functions: Exports `xchk_setup_ag_iallocbt()`, `xchk_iallocbt()`, `xchk_xref_is_not_inode_chunk()`, and `xchk_xref_is_inode_chunk()`. Internal state `struct xchk_iallocbt` tracks seen inode count and expected record sequencing. Key helpers include finobt/inobt xref routines, chunk checks, cluster buffer checks, record alignment validation, rmap btree block and inode extent xrefs, and `xchk_xref_inode_check()`.

Control flow: Setup enables intent draining when needed and initializes AG btree scrub. The record callback decodes each inobt/finobt record, validates record contents, alignment, sparse hole/free masks, inode counts, and cluster-level consistency. Cluster checking maps inode buffers directly, verifies dinode magic and inode numbers, compares btree free bits with incore allocation state or disk `di_mode`, and may request try-harder retry if unfrozen state is ambiguous. Cross-reference paths compare inobt and finobt free/hole state, ensure inode chunks are used space and only owned by inode rmap records, and compare total btree/inode block counts with rmap ownership.

State and persistence: Scrub maintains only transient counters and sequencing expectations. It does not repair or persist changes; corruption is reported through scrub flags and btree cursor state.

Dependencies and integration points: Depends on XFS btree scrub framework, inode allocation btree helpers, inode cache allocation queries, inode buffer mapping, AG headers, rmap/refcount/COW xrefs, sparse inode geometry, and health-driven cross-reference skipping. Repair is handled by `ialloc_repair.c`.

Risks and test signals: Subtle risks include sparse inode holemask interpretation, geometries where one inode chunk spans clusters or one cluster spans chunks, racing inode allocation/free, stale finobt records, and rmap count disagreement. Test sparse and non-sparse filesystems, large block-size inode chunk layouts, all-free/all-allocated finobt omission rules, corrupt inode magic/di_ino, missing or extra rmap ownership, shared/COW staging overlap, pre-try-harder deadlock retries, and both INOBT and FINOBT scrub directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc.c -->
