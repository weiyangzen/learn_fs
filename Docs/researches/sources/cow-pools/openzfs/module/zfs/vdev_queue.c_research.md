# File Research: sources/cow-pools/openzfs/module/zfs/vdev_queue.c

## Purpose
Implements the per-leaf-vdev ZFS I/O scheduler. It queues, prioritizes, throttles, aggregates, dispatches, completes, and reprioritizes physical ZIOs across sync read/write, async read/write, scrub, removal, initializing, trim, and rebuild classes.

## Main Responsibilities
- Maintain per-priority FIFO or AVL queues and active counts.
- Enforce global per-vdev active I/O limits and per-class min/max active limits.
- Dynamically adjust async write concurrency based on dirty data and pending sync tasks.
- Throttle non-interactive I/O while interactive I/O is active using NIA credit/delay rules.
- Aggregate adjacent read/write I/Os into a delegated parent I/O using gang ABDs.
- Optionally bypass queueing for selected scheduler modes and non-rotating block devices.
- Provide queue length, last offset, class length, and pool-busy helpers used elsewhere.

## Key Entry Points
- `vdev_queue_init()`, `vdev_queue_fini()`: create/destroy per-class lists/trees, offset trees, active list, and lock.
- `vdev_queue_io()`: normalize priority, enqueue or bypass an I/O, and return the next dispatchable I/O.
- `vdev_queue_io_done()`: remove a completed active I/O and dispatch more queued work.
- `vdev_queue_change_io_priority()`: reprioritize queued or not-yet-queued I/O.
- `vdev_queue_pool_busy()`: reports whether dirty data has crossed the async write minimum threshold.
- `vdev_queue_length()`, `vdev_queue_last_offset()`, `vdev_queue_class_length()`: queue introspection helpers.

## Important Algorithms and Semantics
- FIFO classes are sync read, sync write, and trim. Other queueable classes use AVL ordering by coarse timestamp bucket and offset, preserving fairness while encouraging locality.
- `vdev_queue_class_to_issue()` first tries classes below their minimum active count using round-robin from the last priority, then tries classes below their maximum active count in priority order.
- `vdev_queue_max_async_writes()` linearly interpolates async write active limits between configured dirty-data percentages, and immediately uses the maximum when dirty data is high or sync tasks are pending.
- Scrub, removal, initializing, and rebuild are non-interactive. Their max concurrency is reduced while interactive I/O is active, and gradually expands only after enough non-interactive completions when the vdev is idle.
- `vdev_queue_aggregate()` merges sufficiently adjacent reads or writes with matching aggregation-inherited flags. Reads may bridge configured gaps; writes may include optional gap-closing I/Os. The aggregate uses a gang ABD to avoid data copies.
- Aggregated parent I/Os are marked `ZIO_FLAG_DONT_QUEUE`; child parent links are bypassed/executed so completion is coordinated through ZIO graph mechanics.
- `ZIO_FLAG_NODATA` I/Os are still queued because bypass code cannot handle some gang ABD and RAIDZ aggregation cases; if selected directly, they are bypassed and completed immediately.

## Data and State
- `vdev_queue_t` owns per-class queues, read/write offset AVL trees, an active list, active counts, last issued offset, NIA counters, and a mutex.
- `vq_cqueued` is a bitmask of non-empty classes.
- `vq_cactive[]` and `vq_active` track active I/Os.
- `vq_ia_active` tracks active interactive I/O.
- `vq_nia_credit` controls how many non-interactive I/Os may proceed around interactive load.
- `vq_last_offset` is used by both scheduler locality and mirror load scoring.

## Tunables
The file exposes module parameters for aggregation limits, read/write gap limits, total max active, dirty-data async-write thresholds, per-class min/max active counts, and NIA credit/delay. Defaults favor high sync read/write concurrency, bounded async writes, and conservative scrub/removal/initializing/rebuild concurrency.

## Dependencies
Uses ZIO, vdev internals, AVL/list primitives, DSL pool dirty data, metaslab/spa state, ABD gang buffers, and dRAID assertions. It provides load information consumed by `vdev_mirror.c`.

## Edge Cases and Failure Handling
- Queueing can be bypassed with `ZIO_FLAG_DONT_QUEUE`, explicit scheduler-off mode, or auto mode for non-rotating block devices.
- Priority normalization prevents read/write child I/Os from inheriting incompatible parent priorities.
- Aggregation refuses TRIM, disabled aggregation, zero aggregation limit, oversize spans, and dRAID distributed-spare queues.
- Locking is carefully managed around aggregate dispatch to avoid `vq_lock` and ZIO lock order inversions.
- Queue length and last offset accessors intentionally avoid locking for performance, accepting possible transient inaccuracy on 32-bit platforms.
