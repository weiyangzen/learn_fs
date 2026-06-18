<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.c

Purpose: Provides common online-repair infrastructure for staging, allocating, bulk-loading, committing, or cancelling replacement btrees.

Important APIs, types, and functions: Exports initialization helpers for bare, AG-rooted, inode-fork, and metadir-inode btrees; `xrep_newbt_alloc_blocks()`, `xrep_newbt_add_extent()`, `xrep_newbt_claim_block()`, `xrep_newbt_commit()`, `xrep_newbt_cancel()`, and `xrep_newbt_unused_blocks()`. Internal helpers estimate bulk-load slack, validate allocation hints, allocate per-AG or file blocks, track reservations with autoreap, and free unused extents.

Control flow: Callers initialize `xrep_newbt` with owner info, allocation hint, reservation class, fake root storage, and bload geometry. They compute btree geometry, reserve the required number of blocks, and provide `xrep_newbt_claim_block()` to the btree bulk loader. Each claim consumes a block from the reservation list, rotates exhausted reservations, fills short or long btree pointers, and relogs deferred frees. Commit cancels autoreap for used blocks and frees unused tails through EFIs; cancel commits autoreap for all reservations so blocks are freed. Cleanup rolls deferred work periodically to avoid exceeding transaction reservation limits.

State and persistence: Tracks reserved extents in memory with perag references, used counts, and autoreap handles. Durable changes occur indirectly when callers commit staged btree roots; `newbt` ensures unused or cancelled allocations are freed or autoreaped and frees fake inode fork memory.

Dependencies and integration points: Depends on XFS allocation, deferred frees, btree staging/bulk-load, owner/rmap metadata, per-AG reservations, scrub repair transaction rolling, and inode fork caches. Used by inode btree repair and other online rebuilders.

Risks and test signals: Key risks are leaking blocks on cancellation or crash, using blocks from the wrong AG for per-AG btrees, bad slack under low space, reservation-class mistakes, and incorrect fake fork cleanup. Test ENOSPC during allocation, cancellation before any block is used, partial use with unused tail freeing, file-based vs per-AG allocation hints, custom allocation callbacks, low-free-space slack, long and short btree pointers, shutdown cleanup behavior, and EFI roll thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/newbt.c -->
