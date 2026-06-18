# Group Research: group_688_linux_sources_os_linux_linux_block_blk_ia_ranges_c_sources_os_linux__cf89c55a5b8c

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-ia-ranges.c -->
# File Research: sources/os/linux/linux/block/blk-ia-ranges.c

## Summary
Implements block-device independent access range registration, validation, replacement, and sysfs exposure. These ranges describe disk LBA regions that can be accessed independently, such as concurrent positioning ranges.

## Main Responsibilities
- Allocate `struct blk_independent_access_ranges` arrays for a disk.
- Validate that ranges are non-empty, contiguous, non-overlapping, sorted by LBA, and exactly cover disk capacity.
- Register `/sys/block/<disk>/queue/independent_access_ranges/<n>/` entries.
- Expose each range’s `sector` and `nr_sectors`.
- Replace or clear a disk’s current range set during setup or revalidation.

## Key APIs
- `disk_alloc_independent_access_ranges()`.
- `disk_set_independent_access_ranges()`.
- `disk_register_independent_access_ranges()`.
- `disk_unregister_independent_access_ranges()`.

## Important Behavior
`disk_check_ia_ranges()` sorts the caller-provided range array in-place by repeatedly finding the range that starts at the next expected sector. It rejects holes, overlaps, zero range count, and a final sector count that does not match `get_capacity(disk)`.

`disk_set_independent_access_ranges()` holds `q->sysfs_lock`, frees invalid or unchanged new ranges, unregisters the old range set, installs the new one, and registers it immediately if the queue is already registered.

Sysfs lifetime is parent-owned: individual range kobjects have a no-op release because the whole flexible array is freed from the parent `blk_independent_access_ranges` kobject release after all children have been deleted.

## State and Synchronization
All public mutation paths use `q->sysfs_lock`. `disk->ia_ranges` is the single owning pointer until sysfs registration transfers final free responsibility to kobject release.

## Risks
The range array is modified during validation, so callers must not depend on original order after `disk_set_independent_access_ranges()`. Lifetime depends on deleting every child kobject before parent release; skipping unregister would leave sysfs references to memory owned by the range set.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-ia-ranges.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-integrity.c -->
# File Research: sources/os/linux/linux/block/blk-integrity.c

## Summary
Implements block-layer data integrity metadata support for requests, including integrity scatterlist accounting, user metadata mapping, merge checks, metadata capability reporting, and sysfs attributes.

## Main Responsibilities
- Count integrity metadata scatterlist segments for a bio.
- Report logical block metadata capabilities through `FS_IOC_GETLBMD_CAP`.
- Map user-provided integrity metadata into a request.
- Decide whether integrity metadata allows request or bio merges.
- Expose integrity format and policy controls under the queue integrity sysfs group.

## Key APIs
- `blk_rq_count_integrity_sg()`.
- `blk_get_meta_cap()`.
- `blk_rq_integrity_map_user()`.
- `blk_integrity_merge_rq()`.
- `blk_integrity_merge_bio()`.
- `blk_integrity_profile_name()`.
- `blk_integrity_attr_group`.

## Important Behavior
Integrity merge checks require both sides either to have integrity metadata or not, matching `bip_flags`, matching application tag when `BIP_CHECK_APPTAG` is set, no integrity gap violation, and a segment count within `max_integrity_segments`.

`blk_get_meta_cap()` translates `struct blk_integrity` into userspace logical block metadata capability fields: integrity/ref-tag support, interval, metadata size, PI tuple size and offset, opaque metadata layout, checksum type, app tag size, and reference tag size.

Sysfs `read_verify` and `write_generate` are inverted relative to internal flags: writing true clears `BLK_INTEGRITY_NOVERIFY` or `BLK_INTEGRITY_NOGENERATE`. Updates are committed through frozen queue-limit updates.

## State and Synchronization
Integrity policy lives in `queue->limits.integrity`. Sysfs writes use `queue_limits_start_update()` and `queue_limits_commit_update_frozen()` to update limits safely.

## Risks
The sysfs boolean inversion is easy to misread. Merge correctness depends on all integrity fields staying aligned with the data request; incorrect segment counts or missed gap checks can create driver-visible metadata layout errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-integrity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-ioc.c -->
# File Research: sources/os/linux/linux/block/blk-ioc.c

## Summary
Manages per-task block I/O contexts and optional per-queue `io_cq` associations used by block schedulers and I/O priority handling.

## Main Responsibilities
- Allocate, reference, share, and release `struct io_context`.
- Preserve I/O priority across task copy when appropriate.
- Implement permission and LSM checks for `set_task_ioprio()`.
- Manage `io_cq` objects that connect one `io_context` to one request queue.
- Tear down `io_cq` state on task exit or queue removal.

## Key APIs
- `put_io_context()`.
- `exit_io_context()`.
- `set_task_ioprio()`.
- `__copy_io()`.
- `ioc_clear_queue()`.
- `ioc_lookup_icq()`.
- `ioc_find_get_icq()`.

## Important Behavior
`io_context` has both `refcount` and `active_ref`. `active_ref` tracks task users; final active release exits all `io_cq`s before dropping the object reference.

With `CONFIG_BLK_ICQ`, `io_cq`s are stored in both an `ioc->icq_tree` indexed by queue id and queue-local `q->icq_list`. A cached RCU hint speeds issue-path lookup. Creation locks `q->queue_lock` before `ioc->lock`.

Release may need the reverse lock order while already holding queue-related locks, so final `io_cq` destruction can be punted to `system_power_efficient_wq`.

## State and Synchronization
Uses task locks for `task->io_context`, atomic reference counters, RCU for lookup hints and delayed `io_cq` freeing, `ioc->lock`, `q->queue_lock`, radix trees, and hlist/list membership.

## Risks
The lock ordering is subtle: destruction must coordinate `ioc->lock`, `q->queue_lock`, RCU protection, and queue lifetime. `set_task_ioprio()` has both credential and security-hook enforcement; bypassing it would skip intended authorization.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-ioc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-iocost.c -->
# File Research: sources/os/linux/linux/block/blk-iocost.c

## Summary
Implements the cgroup v2 `io.cost` controller, an rq-qos policy that estimates I/O cost in virtual device time and distributes device capacity proportionally across cgroups while adapting to observed latency and queue saturation.

## Main Responsibilities
- Maintain a per-device `struct ioc` rq-qos controller.
- Maintain per-device-cgroup `struct ioc_gq` scheduling state.
- Estimate read/write cost using a linear model with sequential/random and per-page coefficients.
- Throttle bios by virtual-time budget, or account unavoidable bios as debt.
- Dynamically adjust virtual-time rate from request wait and completion-latency signals.
- Donate unused cgroup weight to active cgroups that can use capacity.
- Expose cgroup files `io.weight`, `io.cost.qos`, and `io.cost.model`.

## Key APIs and Hooks
- rq-qos hooks: `ioc_rqos_throttle()`, `ioc_rqos_merge()`, `ioc_rqos_done_bio()`, `ioc_rqos_done()`, `ioc_rqos_queue_depth_changed()`, `ioc_rqos_exit()`.
- Initialization: `blk_iocost_init()`, `ioc_init()`, `ioc_exit()`.
- blkcg policy hooks: `ioc_cpd_alloc()`, `ioc_pd_alloc()`, `ioc_pd_init()`, `ioc_pd_free()`, `ioc_pd_stat()`.
- cgroup operations: `ioc_weight_write()`, `ioc_qos_write()`, `ioc_cost_model_write()`.

## Important Behavior
Each bio receives an absolute cost from the linear model. The cost is scaled by inverse hierarchical in-use weight, so lower-share cgroups consume their local virtual-time budget faster. If the cgroup has enough budget, `iocg_commit_bio()` advances `iocg->vtime` and stores `bio->bi_iocost_cost`; completion advances `done_vtime`.

If a bio is over budget, normal issuers sleep on the cgroup wait queue until enough virtual time is available. Bios that must issue as root or when the task has a fatal signal are charged as `abs_vdebt`; the controller later pays debt from the cgroup’s budget and may induce blkcg delay.

The period timer collects latency/rq-wait stats, deactivates idle groups, wakes oversleeping waiters, updates usage stats, transfers surplus weight, adjusts vrate, refreshes automatic parameters, and forgives debt when the device is sufficiently idle.

## Configuration Model
Automatic presets distinguish HDD, queue-depth-one SSD, default SSD, and fast SSD. Users can override QoS targets and model coefficients. `io.cost.qos` can enable/disable the controller and set latency percentiles and min/max vrate. `io.cost.model` sets linear read/write bandwidth and IOPS coefficients.

## State and Synchronization
Per-device state uses `ioc->lock`, a period timer, seqcount-protected period timestamps, percpu latency counters, active cgroup lists, hweight generations, and atomic virtual-time fields. Per-cgroup state uses wait queues, hrtimers, percpu usage counters, hierarchy ancestor arrays, active/surplus/walk lists, debt/delay fields, and cached hierarchical weights.

## Risks
This file has high concurrency and arithmetic complexity. Correctness depends on synchronized hweight propagation, wait queue locking, debt ownership of `inuse`, timer-driven state transitions, and careful unit conversions between wall time, virtual time, percentages, and ppm. Lazy initialization from cgroup writes means rq-qos hooks must tolerate bios before policy activation is complete.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-iocost.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-iolatency.c -->
# File Research: sources/os/linux/linux/block/blk-iolatency.c

## Summary
Implements the cgroup `io.latency` controller, an rq-qos policy that protects configured latency targets by throttling peer cgroups through queue-depth limits and induced delay.

## Main Responsibilities
- Track per-cgroup I/O latency over rolling windows.
- Walk the blkcg hierarchy on bio submission and completion.
- Limit in-flight bios through `rq_wait` queue-depth throttling.
- Scale sibling cgroup queue depths up or down based on protected group latency.
- Apply blkcg induced delay when queue depth is already at one and root-issued work is still causing pressure.
- Expose the cgroup `io.latency` file.

## Key APIs and Hooks
- rq-qos hooks: `blkcg_iolatency_throttle()`, `blkcg_iolatency_done_bio()`, `blkcg_iolatency_exit()`.
- Initialization: `blk_iolatency_init()`, `iolatency_init()`, `iolatency_exit()`.
- cgroup file handlers: `iolatency_set_limit()`, `iolatency_print_limit()`.
- blkcg policy hooks: `iolatency_pd_alloc()`, `iolatency_pd_init()`, `iolatency_pd_offline()`, `iolatency_pd_free()`, `iolatency_pd_stat()`.

## Important Behavior
On submission, the controller walks from the bio’s blkg up to root, checks whether each group needs scale updates, and acquires an in-flight slot. Root-issued or fatal-signal bios bypass sleeping but still increment inflight accounting.

On completion, it walks the same hierarchy, decrements inflight counts, records latency for configured groups, and periodically evaluates whether latency is within target. Rotational devices use mean latency statistics; SSDs use a simple missed/total percentile-like threshold.

When a protected group misses target, its parent’s `scale_cookie` is reduced so peers observe a scale-down event and lower `max_depth`. When conditions improve, the cookie scales back toward `DEFAULT_SCALE_COOKIE`; reaching default clears delay and restores unlimited depth.

## State and Synchronization
`struct blk_iolatency` holds the rq-qos object, enable timer, enable count, and async enable work. Each `iolatency_grp` has percpu latency stats, current window stats, `rq_wait`, `max_depth`, scale cookies, target latency, rolling average, and child latency coordination state.

Enabling or disabling issue-time tracking is deferred to workqueue context and performed with the request queue frozen to keep submission/completion in-flight accounting balanced.

## Risks
The hierarchy walk is intentionally disabled when no cgroup has a latency target; incorrect enable transitions could leak inflight counts. Scale-cookie propagation is distributed and can lag by design. Root-issued metadata/swap work is not counted the same way as ordinary cgroup I/O, so induced delay is essential to avoid priority inversion but can be hard to reason about.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-iolatency.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-ioprio.c -->
# File Research: sources/os/linux/linux/block/blk-ioprio.c

## Summary
Implements a blkcg policy that assigns or constrains bio I/O priority class based on cgroup configuration.

## Main Responsibilities
- Register cgroup files for I/O priority policy.
- Store per-cgroup priority policy.
- Apply policy to each bio before request scheduling.
- Support both cgroup v1 legacy and cgroup v2 default file exposure.

## Key APIs
- `blkcg_set_ioprio()`.
- cgroup file `prio.class`.
- Policy lifecycle: `ioprio_init()`, `ioprio_exit()`.

## Important Behavior
Supported policies are `no-change`, `promote-to-rt`, `restrict-to-be`, `idle`, and `none-to-rt`. `none-to-rt` is treated as an alias for promotion to realtime.

Promotion changes non-RT bios to `IOPRIO_CLASS_RT` with priority level 4. Restriction and idle use `max_t()` over encoded `bi_ioprio`, relying on Linux I/O priority encoding where higher numeric values usually mean lower priority except for `IOPRIO_CLASS_NONE`.

## State and Synchronization
Per-cgroup state is a small `struct ioprio_blkcg` allocated as blkcg policy data. Writes replace the enum policy value directly from kernfs context.

## Risks
Policy behavior depends on encoded I/O priority ordering. This policy affects writeback I/O associated with cgroups, unlike task-only `ioprio_set()`, so cgroup placement directly changes background filesystem writeback priority.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-ioprio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-ioprio.h -->
# File Research: sources/os/linux/linux/block/blk-ioprio.h

## Summary
Declares the block cgroup I/O priority hook used to apply cgroup priority policy to bios.

## Main Contents
- Forward declarations for `struct request_queue` and `struct bio`.
- `blkcg_set_ioprio(struct bio *bio)` declaration when `CONFIG_BLK_CGROUP_IOPRIO` is enabled.
- No-op inline fallback when the feature is disabled.

## Important Behavior
The header lets block submission code call `blkcg_set_ioprio()` unconditionally while compiling out all behavior when cgroup I/O priority support is not configured.

## Risks
The fallback silently does nothing, so callers must not rely on priority modification unless the config option is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-ioprio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-lib.c -->
# File Research: sources/os/linux/linux/block/blk-lib.c

## Summary
Provides generic block-device helper functions for issuing discard, write-zeroes, explicit zero-page writes, zeroout, and secure erase operations as chains of bios.

## Main Responsibilities
- Split discard bios on granularity and maximum bio size constraints.
- Submit discard requests and normalize `-EOPNOTSUPP` for discard.
- Prefer hardware `WRITE ZEROES` for zeroout when available.
- Fall back to writing the shared zero folio unless disabled.
- Submit secure erase requests respecting device limits and alignment.

## Key APIs
- `blk_alloc_discard_bio()`.
- `__blkdev_issue_discard()`.
- `blkdev_issue_discard()`.
- `__blkdev_issue_zeroout()`.
- `blkdev_issue_zeroout()`.
- `blkdev_issue_secure_erase()`.

## Important Behavior
Discard splitting aligns subsequent bios to discard granularity and rounds sizes down when possible. Zeroout validates logical-block alignment and read-only state before issuing I/O.

`blkdev_issue_zeroout()` first tries `REQ_OP_WRITE_ZEROES` when the queue advertises support. If that path reports unsupported, it falls back to explicit zero-page writes unless `BLKDEV_ZERO_NOFALLBACK` was requested.

Killable zeroing checks `fatal_signal_pending(current)` in the loop and stops generating more bios. Long loops call `cond_resched()` to avoid soft lockups.

## State and Synchronization
The helpers use local bio chains and `blk_plug` batching. They do not own persistent state; behavior is driven by current block-device limits and flags.

## Risks
Several limits may change at runtime, especially write-zeroes support after SCSI errors. Callers must pass aligned sector ranges for zeroout and secure erase. Fallback zero-page writes can be much more expensive than hardware zeroing.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-lib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-map.c -->
# File Research: sources/os/linux/linux/block/blk-map.c

## Summary
Maps userspace, kernel, and iterator buffers into bios attached to passthrough block requests, using direct page mapping when safe and bounce/copy buffers otherwise.

## Main Responsibilities
- Deep-copy user iovec metadata for completion-time unmap.
- Copy user data into allocated bio pages when direct mapping is unsafe.
- Pin/map user iterator pages directly when alignment and queue limits allow.
- Map kernel buffers directly or through bounce pages.
- Append mapped bios to passthrough requests while checking queue limits.
- Unmap and copy read data back to userspace after I/O completion.

## Key APIs
- `blk_rq_append_bio()`.
- `blk_rq_map_user_iov()`.
- `blk_rq_map_user()`.
- `blk_rq_map_user_io()`.
- `blk_rq_unmap_user()`.
- `blk_rq_map_kern()`.

## Important Behavior
`blk_rq_map_user_iov()` chooses copy mode for supplied `rq_map_data`, DMA alignment mismatch, non-user-backed iterators, virtual-boundary gap risk, or bvec limit mismatch. ITER_BVEC may be reused directly, but falls back to copying if request limits would require splitting.

`blk_rq_append_bio()` rejects bios that cannot fit request hardware limits without splitting, verifies merge constraints for appended bios, updates request segment counts and data length, and transfers bio crypto context ownership as needed.

For copied user reads, `bio_uncopy_user()` copies data back only if still in process context with an `mm`; orphaned workqueue completions return `-EINTR` instead of copying into an arbitrary address space.

## State and Synchronization
Request-local bio chains carry mapping state. `bio_map_data` tracks copied iterator state, whether pages are owned by the mapping code, and whether the mapping is null-mapped.

## Risks
Cleanup paths must distinguish pinned user pages, copied pages, integrity mappings, vmalloc mappings, and null-mapped data. The caller must pass the original bio chain to `blk_rq_unmap_user()` because request completion may change `rq->bio`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-merge.c -->
# File Research: sources/os/linux/linux/block/blk-merge.c

## Summary
Implements bio splitting to queue limits and bio/request merge logic for the block layer, including segment accounting, gap checks, discard merging, scheduler merging, rq-qos merge charging, integrity, crypto, cgroup, zoned, and atomic-write constraints.

## Main Responsibilities
- Determine where bios must split to satisfy queue limits.
- Split discard, read/write, zone append, and write-zeroes bios.
- Recalculate request physical segment counts.
- Check back, front, and discard merge eligibility.
- Merge bios into requests and requests into adjacent requests.
- Preserve accounting, tracing, crypto, integrity, and mixed failfast state.

## Key APIs
- `bio_submit_split_bioset()`.
- `bio_split_discard()`.
- `bio_split_io_at()`.
- `bio_split_rw()`.
- `bio_split_zone_append()`.
- `bio_split_write_zeroes()`.
- `bio_split_to_limits()`.
- `blk_recalc_rq_segments()`.
- `ll_back_merge_fn()`.
- `blk_attempt_req_merge()`.
- `blk_rq_merge_ok()`.
- `blk_try_merge()`.
- `bio_attempt_back_merge()`.
- `blk_attempt_plug_merge()`.
- `blk_bio_list_merge()`.
- `blk_mq_sched_try_merge()`.

## Important Behavior
Splitting checks DMA alignment, crypto data unit alignment, segment count, maximum bytes, maximum sectors, physical/logical block alignment, virtual boundary gaps, atomic-write restrictions, and `REQ_NOWAIT`. If a split is required for polled I/O, polling is cleared to avoid direct-I/O iopoll hangs.

Merge checks reject incompatible operations, cgroups, integrity metadata, crypto contexts, write hints, write streams, I/O priorities, atomic-write flags, queue boundary limits, segment limits, and gap constraints. Zoned write plugging blocks front merges to sequential zones.

Mixed failfast merges propagate per-request failfast flags down into each bio and mark `RQF_MIXED_MERGE`, because the merged request can no longer represent one uniform failfast setting.

## State and Synchronization
Request merge operations update bio chains, `biotail`, `__sector`, `__data_len`, physical and integrity segment counts, `phys_gap_bit`, accounting counters, crypto keyslots, and scheduler/elevator state. Plug merging deliberately avoids elevator callbacks because plugged requests are not yet on the scheduler.

## Risks
This is a central correctness boundary: accepting a bad merge can violate driver DMA limits or semantic constraints, while rejecting too much hurts performance. Atomic writes and zone append/write-plugged writes are especially sensitive because splitting or reordering can break their semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-merge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq-cpumap.c -->
# File Research: sources/os/linux/linux/block/blk-mq-cpumap.c

## Summary
Provides helper functions for sizing and building CPU-to-hardware-queue maps for blk-mq devices.

## Main Responsibilities
- Calculate queue counts from possible or online CPU masks.
- Evenly map CPUs to hardware queues.
- Map queues from device/bus IRQ affinity when available.
- Find a representative NUMA node for a hardware queue.

## Key APIs
- `blk_mq_num_possible_queues()`.
- `blk_mq_num_online_queues()`.
- `blk_mq_map_queues()`.
- `blk_mq_hw_queue_to_node()`.
- `blk_mq_map_hw_queues()`.

## Important Behavior
`blk_mq_map_queues()` uses `group_cpus_evenly()` to spread CPUs across the requested number of queues. If grouping fails, every possible CPU maps to `queue_offset`.

`blk_mq_map_hw_queues()` first asks the device bus for IRQ affinity masks. If the bus lacks `irq_get_affinity()` or any queue has no mask, it falls back to the generic even mapping.

## State and Synchronization
The file only fills caller-provided `struct blk_mq_queue_map` arrays during queue setup. There is no persistent state.

## Risks
Fallback behavior is coarse and may place all CPUs on one queue if CPU grouping allocation fails. Reverse node lookup is linear over possible CPUs and intended only for initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq-cpumap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq-debugfs.c -->
# File Research: sources/os/linux/linux/block/blk-mq-debugfs.c

## Summary
Implements debugfs support for blk-mq queues, hardware contexts, software contexts, schedulers, rq-qos policies, tags, flags, and request lists.

## Main Responsibilities
- Create queue-level debugfs files such as `state`, `pm_only`, `requeue_list`, and `zone_wplugs`.
- Expose hardware-context state, flags, dispatch lists, busy requests, tag bitmaps, active count, and type.
- Expose per-CPU context request lists.
- Register scheduler and rq-qos debugfs subdirectories and attributes.
- Format request operations, command flags, rq flags, tags, and state.

## Key APIs
- `__blk_mq_debugfs_rq_show()`.
- `blk_mq_debugfs_rq_show()`.
- `blk_mq_debugfs_register()`.
- `blk_mq_debugfs_register_hctx()`.
- `blk_mq_debugfs_unregister_hctx()`.
- `blk_mq_debugfs_register_hctxs()`.
- `blk_mq_debugfs_unregister_hctxs()`.
- `blk_mq_debugfs_register_sched()`.
- `blk_mq_debugfs_unregister_sched()`.
- `blk_mq_debugfs_register_sched_hctx()`.
- `blk_mq_debugfs_unregister_sched_hctx()`.
- `blk_mq_debugfs_register_rq_qos()`.

## Important Behavior
The queue `state` file accepts `run`, `start`, and `kick`, which invoke `blk_mq_run_hw_queues()`, `blk_mq_start_stopped_hw_queues()`, and `blk_mq_kick_requeue_list()`. It refuses writes once the queue is dying.

Request-list seq files lock the relevant list while iterating: `q->requeue_lock`, `hctx->lock`, or `ctx->lock`. Busy request reporting uses `blk_mq_tagset_busy_iter()` under `q->elevator_lock`.

`debugfs_create_files()` asserts `q->debugfs_mutex` and also asserts that `elevator_lock` and `rq_qos_mutex` are not held, avoiding lock nesting under locks that may be acquired while a queue is frozen.

## State and Synchronization
Debugfs dentries are stored on queues and hardware contexts. Registration and scheduler/rq-qos directory creation are serialized by `q->debugfs_mutex`; individual readers use the locks appropriate to the data they expose.

## Risks
Debugfs output observes live request state, so request state may change during reads. The writeable `state` operation is diagnostic but can actively kick queues, so it must remain unavailable after queue teardown begins.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq-debugfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq-debugfs.h -->
# File Research: sources/os/linux/linux/block/blk-mq-debugfs.h

## Summary
Declares blk-mq debugfs attribute structures and registration functions, with no-op fallbacks when debugfs support is disabled.

## Main Contents
- `struct blk_mq_debugfs_attr`, containing name, mode, show callback, write callback, and optional seq operations.
- Request display helpers.
- Queue, hctx, scheduler, scheduler-hctx, and rq-qos debugfs registration functions.
- `queue_zone_wplugs_show()` declaration or no-op fallback.

## Important Behavior
When `CONFIG_BLK_DEBUG_FS` is disabled, all registration functions compile to empty inline functions. Zoned write plug debug display is available only with both zoned block device and block debugfs support.

## Risks
Code using these helpers must not depend on debugfs side effects. Attribute definitions must set either `.show` or `.seq_ops` consistently because the implementation treats seq-only attributes as read-only.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq-debugfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-mq-dma.c -->
# File Research: sources/os/linux/linux/block/blk-mq-dma.c

## Summary
Maps blk-mq request payloads and integrity metadata into physical vectors, DMA address iterators, and scatterlists, including support for P2PDMA and IOVA-based DMA mapping.

## Main Responsibilities
- Iterate request bio chains as mergeable physical segments.
- Map request payload segments to DMA addresses one at a time.
- Use PCI P2PDMA bus-address mappings when possible.
- Use IOVA-based DMA coalescing when segment gap and DMA merge-boundary constraints allow.
- Fall back to direct `dma_map_phys()` per segment.
- Build scatterlists for request payload and integrity metadata.

## Key APIs
- `blk_rq_dma_map_iter_start()`.
- `blk_rq_dma_map_iter_next()`.
- `__blk_rq_map_sg()`.
- `blk_rq_integrity_dma_map_iter_start()`.
- `blk_rq_integrity_dma_map_iter_next()`.
- `blk_rq_map_integrity_sg()`.

## Important Behavior
`blk_map_iter_next()` walks a request’s special payload, data bio chain, or integrity bio vectors and coalesces adjacent physical vectors when queue limits and `biovec_phys_mergeable()` allow. Segment length is capped by `get_max_segment_size()`.

DMA mapping starts by examining the first segment for P2PDMA state. Bus-address P2PDMA returns the bus address directly. Host-bridge P2PDMA uses `DMA_ATTR_MMIO` with normal DMA mapping. If IOVA mapping is suitable, the code allocates one IOVA span, links all segments, syncs it, and returns one coalesced DMA range.

Scatterlist mapping forces clearing stale sg termination bits before appending the next element, so drivers that reuse sg tables do not need to fully reinitialize them for every request.

## State and Synchronization
Mapping state is carried by caller-provided `struct dma_iova_state` and `struct blk_dma_iter`. The iterator stores current bio, bvec array, bvec iterator, integrity/data mode, P2PDMA state, DMA address, length, and status.

## Risks
The IOVA path depends on the request’s physical gap mask being compatible with the DMA device merge boundary. Error handling must destroy partially linked IOVA state. Segment counts are checked against request physical segment accounting; mismatches indicate earlier split/merge accounting bugs.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-mq-dma.c -->