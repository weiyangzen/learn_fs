<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc_repair.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc_repair.c

Purpose: Rebuilds both inode allocation btrees for an AG from reverse-mapping records and inode cluster contents.

Important APIs, types, and functions: `struct xrep_ibt` tracks the reconstructed record under construction, staged new inobt/finobt (`xrep_newbt`), old inode btree blocks, an `xfarray` of inode records, inode/free counts, finobt record count, and array cursor. Public functions are `xrep_iallocbt()` and `xrep_revalidate_iallocbt()`. Core helpers process rmap records, read inode clusters, construct free/hole masks, bulk-load staged btrees, reset AGI counters, reap old btree blocks, and revalidate.

Control flow: Repair requires rmapbt. It allocates an xfarray sized for maximum AG inode records, scans all AG rmaps for `OWN_INODES` and `OWN_INOBT`, records old btree blocks for later reaping, validates inode extents against geometry and free-space btrees, reads each inode cluster directly, derives in-use state from incore inode allocation or disk dinode mode, and appends normalized inobt records. It then checks record ordering, uses `xrep_newbt` and btree bulk loading to stage new inobt and finobt roots, commits staged roots into the AGI, recalculates AGI counts and perag state, commits unused newbt reservations, rolls the AG transaction, and reaps old inode-btree blocks.

State and persistence: New btree blocks are allocated and tracked with autoreap until committed. The durable change is replacement of AGI btree roots and levels plus AGI inode/free counters; old btree blocks are freed after the new roots are logged. Repair also forces filesystem summary counter recalculation and may request per-AG reservation reset for finobt.

Dependencies and integration points: Depends on rmapbt correctness, free-space btrees, inode cluster buffer reads, sparse inode geometry, `xfarray`, `xagb_bitmap`, btree staging/bulk-load APIs, `newbt.c`, reap helpers, AG transaction rolling, and health masks for both INOBT and FINOBT.

Risks and test signals: Risks include rebuilding from corrupt rmap data, losing old btree blocks before new roots are durable, wrong free/hole mask derivation from uncached inodes, finobt record filtering, block reservation ENOSPC, and geometries with sparse or multi-record clusters. Test rmap-less refusal, dense and sparse inode AGs, corrupt inode extent alignment, all-free/all-used chunks, finobt disabled/enabled with reservations, ENOSPC mid-build cancellation, crash after staged root commit but before reaping, summary counter recalculation, and post-repair revalidation of both btrees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ialloc_repair.c -->
