<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.c

## Purpose
`dm-bio-prison-v2.c` implements the newer DM bio prison with shared and exclusive lock levels, quiescing, and detained-bio handoff on unlock.

## Important APIs, Types, And Functions
`struct dm_bio_prison_v2` holds a workqueue, global spinlock, rbtree, and cell mempool. APIs include create/destroy, cell alloc/free, `dm_cell_get_v2()`, `dm_cell_put_v2()`, `dm_cell_lock_v2()`, `dm_cell_quiesce_v2()`, `dm_cell_lock_promote_v2()`, and `dm_cell_unlock_v2()`. Internal helpers compare overlapping keys, find/insert cells, update shared counts, and erase cells.

## Control Flow
Shared callers acquire with a key and lock level; if an exclusive lock blocks them, their bio is detained. Exclusive callers lock a cell, possibly requiring existing shared users to quiesce. Last shared put queues a continuation when needed. Unlock merges detained bios to the caller and returns whether the cell should be freed.

## State And Persistence
State is runtime-only: rbtrees, shared counts, exclusive flags/levels, detained bios, quiesce continuation, mempool cells, and the caller-provided workqueue.

## Dependencies, Integration Points, Risks, And Test Signals
It depends on DM block/thin key types, bio lists, rbtrees, mempool/slab, spinlocks, and workqueues. Risks include noted starvation, incomplete shared-level tracking, single continuation storage, cell ownership mistakes, and global lock contention. Test shared/exclusive lock matrices, double exclusive `-EBUSY`, quiesce continuation, promotion, detained bio merge, ownership returns, overlapping ranges, and mempool failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.c -->
