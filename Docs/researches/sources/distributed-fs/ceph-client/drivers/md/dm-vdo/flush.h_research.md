# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/flush.h

## Purpose
`flush.h` exposes the VDO flush barrier API and defines `struct vdo_flush`, the completion-backed request object used internally by the flusher.

## Important APIs, Types, And Functions
- `struct vdo_flush` contains a `vdo_completion`, a `bio_list` of covered bios, a `vdo_waiter` link for flusher queues, and a `flush_generation`.
- `struct flusher` is opaque outside `flush.c`.
- Public operations include `vdo_make_flusher()`, `vdo_free_flusher()`, `vdo_get_flusher_thread_id()`, `vdo_complete_flushes()`, `vdo_dump_flusher()`, `vdo_launch_flush()`, `vdo_drain_flusher()`, and `vdo_resume_flusher()`.

## Control Flow And Data Flow
External VDO code creates a flusher during VDO setup, calls `vdo_launch_flush()` for block-layer flush semantics, calls `vdo_complete_flushes()` when logical-zone activity advances enough to acknowledge pending flushes, and uses drain/resume during administrative suspend/resume.

## State And Persistence Behavior
The header exposes only transient flush state. The generation value on `struct vdo_flush` is the logical persistence-order barrier: bios attached to a request are not submitted to the lower device until all relevant in-flight VDO work older than that generation is done.

## Dependencies And Integration Points
The header depends on `funnel-workqueue.h`, `types.h`, `vio.h`, and `wait-queue.h`. It is consumed by VDO core, logical zone, and administrative state code that must coordinate with flush barriers.

## Risks
- `struct vdo_flush` embeds queue linkage and must not be queued on multiple wait queues at once.
- Callers must respect the flusher thread returned by `vdo_get_flusher_thread_id()` for operations that assert thread affinity.
- `vdo_complete_flushes()` must be invoked after logical-zone generation progress or flush bios can remain pending.

## Test Signals
Compile coverage should catch type and completion integration. Runtime tests should verify that suspend/drain users call the API from the correct thread and that `vdo_dump_flusher()` reports expected queue states under pending flushes.
