# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/init.c

This file documents the bcachefs btree architecture and initializes/tears down the btree subsystem workqueues, pools, caches, iterators, key cache, write buffer, and interior-update support.

Core responsibilities:
- Contains a long `DOC_LATEX(btrees)` design document explaining bcachefs as a transactional key-value store over many btrees.
- Documents functional btree groups: core filesystem data, allocation/space management, snapshots/subvolumes, reconcile work, quotas/stripes/LRU/logged ops/accounting.
- Documents key invariants: no duplicate keys, deletion via whiteouts, preserved update ordering, log-structured node bsets, packed keys, and interior pointer semantics.
- Implements `bch2_fs_btree_exit()` to tear down node scan, write buffer, key cache, iterators, interior updates, evicted-size table, node cache, workqueues, mempools, and biosets.
- Implements `bch2_fs_btree_init_early()` for preallocation-free list/work structure initialization.
- Implements `bch2_fs_btree_init()` for read-side and common btree resources: read-complete workqueue, fill-iterator mempool, btree bio set, bounce buffer pool, cache, iterators, key cache, and read-error ratelimits.
- Implements `bch2_fs_btree_init_rw()` for write-side resources: write submit/complete workqueues, interior update machinery, write buffer, and evicted-size tracking.

Important invariants:
- Common btree initialization is split from read-write initialization; write-side workqueues and update machinery are only created when entering RW mode.
- Exit ordering unwinds higher-level services before destroying workqueues/pools they may use.
- The fill iterator size is derived from configured btree node blocks and sort iterator set counts.
- Btree node size drives bounce-pool allocation.

Dependencies:
- Uses btree cache, iterator, interior update, key cache, node scan, read/sort/write/write-buffer subsystems.
- Uses Linux workqueues, mempools, biosets, and ratelimit helpers.

Risk points:
- `bch2_fs_btree_init()` chains several allocations in one condition; partial initialization relies on the broader filesystem init error path calling exit cleanup.
- Workqueue names and flags are part of operational behavior; btree read completion is high priority/freezable/mem-reclaim, and write queues are single-threaded.
- The documented btree invariants are relied on by `commit.c` and `interior.c` rather than enforced locally.
