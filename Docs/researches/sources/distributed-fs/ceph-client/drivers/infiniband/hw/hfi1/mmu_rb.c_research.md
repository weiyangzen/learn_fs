# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mmu_rb.c

## Purpose
`mmu_rb.c` implements an interval-tree cache of user memory ranges tied to Linux MMU notifier invalidations. HFI1 users can register nodes representing pinned or cached memory, search and evict them, and receive asynchronous remove callbacks when the process address space invalidates a range.

## Important APIs, types, and functions
- `hfi1_mmu_rb_register()` allocates a cacheline-aligned `struct mmu_rb_handler`, initializes an interval tree, LRU list, delete list, work item, and MMU notifier, then registers against `current->mm`.
- `hfi1_mmu_rb_unregister()` unregisters the notifier, flushes delete work, removes all nodes, invokes remove callbacks, drops the mm reference, and frees the aligned allocation.
- `hfi1_mmu_rb_insert()` inserts a non-overlapping `struct mmu_rb_node` for the registered `mm`, optionally using `ops->filter` for overlap semantics.
- `hfi1_mmu_rb_get_first()` searches for the first overlapping node and refreshes its LRU position.
- `hfi1_mmu_rb_release()` and internal release callbacks move nodes to deferred removal and queue work.
- `hfi1_mmu_rb_evict()` walks LRU nodes with only the handler reference and lets `ops->evict()` select victims.
- `mmu_notifier_range_start()` removes overlapping nodes during invalidation and defers sleeping remove callbacks to `handle_remove()`.

## Control flow
Users register a handler with callbacks and a workqueue. Insert validates that the current process matches the registered `mm`, checks for an existing matching interval, inserts into the cached interval tree, and appends to LRU. Searches require the caller to hold the handler spinlock and return an overlapping node.

On MMU invalidation, the notifier holds the handler lock, iterates all interval-tree nodes overlapping the invalidated range, removes each from the tree and LRU list, and drops its kref with `release_nolock()`. That callback queues the node on `del_list` and schedules `handle_remove()` so `ops->remove()` can sleep outside the notifier and spinlock context.

Unregister prevents future notifications first, flushes delete work, drains the tree under lock into a local list, and calls `ops->remove()` through `release_immediate()` for each remaining node.

## State and persistence
`struct mmu_rb_handler` owns an MMU notifier, spinlock, cached interval tree, LRU list, deferred delete list, workqueue pointer, callback table, callback argument, and original allocation pointer. `struct mmu_rb_node` stores address, length, cached last address, tree node, list node, handler pointer, and kref. State is per-process-mm runtime state and has no persistence beyond handler lifetime.

## Dependencies and integration points
The file depends on Linux `mmu_notifier`, interval tree macros, rb trees, krefs, workqueues, process `mm` lifetime management, spinlocks, and HFI1 tracepoints. Callers provide HFI1-specific memory-cache callbacks through `struct mmu_rb_ops`.

## Risks
- `ops->filter()` and `ops->evict()` must not sleep because they are called under the handler spinlock.
- `ops->remove()` may sleep, so all paths must avoid invoking it under the spinlock or MMU notifier critical section; the deferred delete path enforces this.
- Current-mm checks mean insert/evict from the wrong process silently fail or return `-EPERM`.
- Address arithmetic uses `addr + len - 1` and page alignment; zero lengths or overflowed ranges would be dangerous if callers pass invalid nodes.
- Kref ownership must be consistent between tree references, external users, eviction, invalidation, and unregister.

## Test signals
- Test overlapping insert rejection with and without a filter callback.
- Trigger `munmap()`, process exit, and invalidation while nodes are referenced, confirming deferred remove callbacks run after references drop.
- Exercise unregister with live nodes, queued delete work, and empty trees.
- Stress LRU eviction under concurrent searches and invalidations with lockdep enabled.
