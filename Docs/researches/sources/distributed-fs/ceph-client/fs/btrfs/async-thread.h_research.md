# sources/distributed-fs/ceph-client/fs/btrfs/async-thread.h

## Purpose
Declares the Btrfs asynchronous workqueue interface and the per-work item structure used by `async-thread.c`. It gives Btrfs subsystems a common way to queue normal work with an optional ordered completion/free phase.

## Important APIs, Types, And Functions
The header forward-declares `struct btrfs_fs_info`, `struct btrfs_workqueue`, and `struct btrfs_work`. It defines callback types `btrfs_func_t(struct btrfs_work *)` and `btrfs_ordered_func_t(struct btrfs_work *, bool)`. `struct btrfs_work` contains the normal callback, optional ordered callback, embedded `work_struct`, ordered-list node, owning workqueue pointer, and private flags.

Declared functions cover allocation of regular and ordered workqueues, work initialization and queueing, destruction, max-active adjustment, owner lookup, congestion query, and flushing.

## Control Flow
Callers embed or allocate a `struct btrfs_work`, initialize it with `btrfs_init_work()`, and enqueue it through `btrfs_queue_work()`. The normal callback runs first. If an ordered callback was supplied, the implementation later calls it with `false` for ordered completion and `true` for final/free handling.

## State And Persistence
The header defines in-memory state only. The comment "Don't touch things below" marks fields owned by the async framework after initialization. Persistence of filesystem changes is the responsibility of caller callbacks and surrounding Btrfs transaction code.

## Dependencies And Integration Points
It depends on Linux `workqueue.h`, `list.h`, compiler annotations, and the implementation in `async-thread.c`. Many Btrfs modules can include it without depending on the private layout of `struct btrfs_workqueue`.

## Risks
Callers must respect object lifetime: work items must remain alive until the async framework invokes the appropriate final callback or completion path. Ordered callbacks must interpret the boolean phase consistently. Direct mutation of internal fields after queueing can break list ordering, workqueue ownership, and flag synchronization.

## Test Signals
Build coverage checks API consistency. Runtime signals come from async-thread tests or Btrfs stress workloads that initialize, queue, flush, and destroy workqueues while validating callback ordering and object lifetime.
