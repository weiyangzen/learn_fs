<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-resv.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-resv.h

## Purpose
Defines reservation objects that hold DMA fences for DMA-BUF, TTM, GEM, and other buffer managers.

## Important APIs, Types, And Functions
Defines `enum dma_resv_usage`, `dma_resv_usage_rw()`, `struct dma_resv`, and `struct dma_resv_iter`. Locking helpers wrap ww_mutex operations. APIs initialize/finalize objects, reserve fence slots, add/replace/copy/get fences, iterate fences locked or unlocked, wait/test by usage, set deadlines, and describe state.

## Control Flow
Writers lock the reservation object, reserve enough slots before point-of-no-return submission, then add fences with usage classifications. Readers either hold the reservation lock or use RCU lockless iterators that may restart. Wait/test helpers gather fences up to the requested usage ordering.

## State And Persistence
State is the ww_mutex lock and RCU fence list. Fence usage ordering is `KERNEL < WRITE < READ < BOOKKEEP`, and queries for one usage include lower usages. This is live synchronization state, not persistent storage.

## Dependencies And Integration Points
Depends on ww_mutex deadlock handling, DMA fences, slab, seqlock/RCU, and DMA-BUF implicit synchronization. It integrates dynamic buffer placement, command submission, and cross-driver buffer sharing.

## Risks And Edge Cases
Lock acquisition can return `-EDEADLK`, requiring callers to drop all locks in the ww acquire context and use slowpath locking. Fence slots must be reserved before adding because add cannot fail. Usage can be promoted but not degraded. Lockless iteration may restart, so accumulated statistics must check `dma_resv_iter_is_restarted()`.

## Test Signals
Tests should cover lock/trylock/interruptible/deadlock slowpath, reservation slot accounting, add and replace by context, usage filtering, lockless iterator restart, wait timeout, signaled tests, deadline propagation, fence copy, and debug max-fence reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-resv.h -->
