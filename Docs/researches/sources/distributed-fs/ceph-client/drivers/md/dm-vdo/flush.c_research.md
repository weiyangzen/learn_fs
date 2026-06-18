# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/flush.c

## Purpose
`flush.c` implements the VDO flusher, which batches incoming flush/FUA bios, advances flush generations through logical zones and the packer, waits until affected VIO activity has retired, and finally submits the flush bios to the backing block device.

## Important APIs, Types, And Functions
- `struct flusher` owns the administrative state, generation counters, notifier and pending queues, flush mempool, waiting bio list, locking, and bio-thread rotor.
- Lifecycle APIs are `vdo_make_flusher()`, `vdo_free_flusher()`, and `vdo_get_flusher_thread_id()`.
- Request path APIs are `vdo_launch_flush()`, `flush_vdo()`, `notify_flush()`, `increment_generation()`, `flush_packer_callback()`, `finish_notification()`, `vdo_complete_flushes()`, and `vdo_complete_flush()`.
- Drain/resume APIs are `vdo_drain_flusher()` and `vdo_resume_flusher()`.
- Allocation helpers use a `mempool_t` with `allocate_flush()` and `free_flush()`, creating `struct vdo_flush` completions.

## Control Flow And Data Flow
`vdo_launch_flush()` is called when an empty flush bio arrives or before acknowledging a non-empty FUA bio. It appends the bio to `waiting_flush_bios` under the flusher spinlock and tries to allocate a `vdo_flush` from a nonblocking mempool. If allocation succeeds, all waiting bios are moved into that flush object and enqueued to the packer thread.

On the flusher thread, `flush_vdo()` asserts normal operation, assigns the next `flush_generation`, enqueues the request on `notifiers`, and starts notification if it is first in line. Notification walks logical zones one at a time with `increment_generation()`, calling `vdo_increment_logical_zone_flush_generation()` on each zone thread. After all logical zones are notified, `flush_packer_callback()` increments the packer flush generation and returns to `finish_notification()`.

`finish_notification()` moves the request from `notifiers` to `pending_flushes`, then calls `vdo_complete_flushes()`. Completion scans all logical zones for the minimum `oldest_active_generation`; pending flushes complete only when their generation is older than every active generation. Completed flushes are requeued to a selected bio thread, where `vdo_complete_flush_callback()` accounts bios, retargets them to the backing device, increments `flush_out`, and calls `submit_bio_noacct()`.

## State And Persistence Behavior
The flusher persists no disk metadata itself, but enforces write-ordering and durability semantics across VDO's in-memory pipeline and the backing device. Generation counters (`flush_generation`, `first_unacknowledged_generation`, `notify_generation`) define the ordering contract. `pending_flushes` tracks generations waiting for active logical-zone work to drain. The mempool ensures at least one flush descriptor can be available under memory pressure, and completed descriptors are reused to launch bios that accumulated after allocation failures.

## Dependencies And Integration Points
The implementation integrates with `admin-state`, `completion`, `io-submitter`, `logical-zone`, `slab-depot`, `vdo`, and the Linux bio/mempool APIs. It uses VDO completion queues for thread handoff, the packer thread as its home thread, logical-zone generation tracking for barriers, and bio threads for final lower-device submission.

## Risks
- Correctness depends on all flusher state transitions running on the packer/flusher thread except the spinlock-protected waiting-bio list.
- Allocation failure is intentionally deferred by keeping bios on `waiting_flush_bios`; regressions in `release_flush()` could strand them.
- Completion ordering assumes `oldest_active_generation` is read consistently enough with `READ_ONCE()` and that logical zones update it correctly.
- Drain completion requires both `pending_flushes` and `waiting_flush_bios` to be empty; missed relaunches can hang suspend.
- `select_bio_queue()` depends on a valid nonzero bio thread count and sane `bio_rotation_interval`.

## Test Signals
Integration tests should stress concurrent flush and FUA bios, forced `GFP_NOWAIT` allocation failure, suspend/drain while flushes are pending, multiple logical zones with long-running VIOs, bio-thread rotation, and read-only transition during `flush_vdo()`. Useful runtime signals are no stuck drain, monotonic generation logs, and correct lower-device flush count.
